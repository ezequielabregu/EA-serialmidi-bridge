import time
import queue
import rtmidi
import serial
import threading
import logging
import sys
from PyQt6 import QtCore, QtWidgets
import serialmidi

class SerialMIDI:
    def __init__(self, gui, serial_port_name, serial_baud, midi_in_name, midi_out_name):
        self.gui = gui  # Reference to the GUI for updating lights
        self.serial_port_name = serial_port_name
        self.serial_baud = serial_baud
        self.given_port_name_in = midi_in_name
        self.given_port_name_out = midi_out_name
        self.thread_running = True
        self.midi_ready = False
        self.midiin_message_queue = queue.Queue()
        self.midiout_message_queue = queue.Queue()
        self.ser = None
        self.midi_in_active = False
        self.midi_out_active = False

    def get_midi_length(self, message):
        if len(message) == 0:
            return 100
        opcode = message[0]
        if opcode >= 0xf4:
            return 1
        if opcode in [0xf1, 0xf3]:
            return 2
        if opcode == 0xf2:
            return 3
        if opcode == 0xf0:
            if message[-1] == 0xf7:
                return len(message)

        opcode = opcode & 0xf0
        if opcode in [0x80, 0x90, 0xa0, 0xb0, 0xe0]:
            return 3
        if opcode in [0xc0, 0xd0]:
            return 2

        return 100

    def serial_writer(self):
        while not self.midi_ready:
            time.sleep(0.1)
        while self.thread_running:
            try:
                message = self.midiin_message_queue.get(timeout=0.4)
            except queue.Empty:
                continue
            if not self.ser or not self.ser.is_open:
                break  # Exit if the serial port is closed
            #uncomment the next line to see the raw data
            #logging.debug(message)
            #logging.debug(describe_midi_message(message))
            self.ser.write(bytearray(message))
            self.gui.led_blink_signal.emit("#f1c40f")  # Serial Port LED (yellow for incoming)

    def serial_watcher(self):
        receiving_message = []
        running_status = 0

        while not self.midi_ready:
            time.sleep(0.1)

        while self.thread_running:
            if not self.ser or not self.ser.is_open:
                break  # Exit if the serial port is closed
            try:
                data = self.ser.read()
            except serial.SerialException:
                break  # Exit gracefully if the serial port is closed
            if data:
                for elem in data:
                    receiving_message.append(elem)
                if len(receiving_message) == 1:
                    if (receiving_message[0] & 0xf0) != 0:
                        running_status = receiving_message[0]
                    else:
                        receiving_message = [running_status, receiving_message[0]]

                message_length = self.get_midi_length(receiving_message)
                if message_length <= len(receiving_message):
                    #uncomment the next line to see the raw data
                    #logging.debug(receiving_message)
                    logging.debug(describe_midi_message(receiving_message))
                    self.midiout_message_queue.put(receiving_message)
                    receiving_message = []
                    # After receiving data (incoming)
                    self.gui.led_blink_signal.emit("#2ecc71")  # Or your serial port LED color

    def reset_activity_flags(self):
        """Reset the activity flags for MIDI In and Out."""
        self.midi_in_active = False
        self.midi_out_active = False

    class midi_input_handler:
        def __init__(self, parent):
            self.parent = parent
            self._wallclock = time.time()

        def __call__(self, event, data=None):
            message, deltatime = event
            self._wallclock += deltatime
            self.parent.midiin_message_queue.put(message)
            # Optionally, blink LED and log
            self.parent.gui.midi_in_led_blink_signal.emit("#f1c40f")  # Yellow
            logging.debug(f"MIDI IN: {describe_midi_message(message)}")

    def midi_watcher(self):
        midiin = rtmidi.MidiIn()
        midiout = rtmidi.MidiOut()

        # Retrieve available MIDI input ports
        available_ports_in = midiin.get_ports()
        available_ports_out = midiout.get_ports()

        logging.info("IN : '" + "','".join(available_ports_in) + "'")
        logging.info("OUT : '" + "','".join(available_ports_out) + "'")
        logging.info("Hit ctrl-c to exit")

        port_index_in = -1
        port_index_out = -1

        if self.given_port_name_in is not None:
            # search and open MIDI IN port
            for i, s in enumerate(available_ports_in):
                if self.given_port_name_in in s:
                    port_index_in = i

        if self.given_port_name_out is not None:
            # search and open MIDI OUT port
            for i, s in enumerate(available_ports_out):
                if self.given_port_name_out in s:
                    port_index_out = i

        if port_index_in == -1 and port_index_out == -1:
            self.thread_running = False
            self.midi_ready = True
            sys.exit()

        if port_index_out != -1:
            midiout.open_port(port_index_out)
        if port_index_in != -1:
            midiin.open_port(port_index_in)
            self.midi_ready = True
            midiin.ignore_types(sysex=False, timing=False, active_sense=False)
            midiin.set_callback(self.midi_input_handler(self))

        try:
            while self.thread_running:
                try:
                    message = self.midiout_message_queue.get(timeout=0.4)
                except queue.Empty:
                    continue

                # Send the MIDI message to the output port
                try:
                    midiout.send_message(message)
                    self.gui.midi_out_led_blink_signal.emit("#2ecc71")  # Green for MIDI OUT
                except Exception as e:
                    logging.error(f"Failed to send MIDI message: {message}. Error: {e}")
        finally:
            # Remove callback and close ports safely
            midiin.cancel_callback()
            if midiin.is_port_open():
                midiin.close_port()
            if midiout.is_port_open():
                midiout.close_port()
            # Do NOT call .delete() here unless you are 100% sure nothing will touch these objects again
            # Let Python's garbage collector handle it after thread exit

    def start(self):
        try:
            self.ser = serial.Serial(self.serial_port_name, self.serial_baud)
        except serial.serialutil.SerialException:
            print("Serial port opening error.")
            logging.error("Serial port opening error.")
            return

        self.ser.timeout = 0.4

        self.s_watcher = threading.Thread(target=self.serial_watcher)
        self.s_writer = threading.Thread(target=self.serial_writer)
        self.m_watcher = threading.Thread(target=self.midi_watcher)

        self.s_watcher.start()
        self.s_writer.start()
        self.m_watcher.start()

        self.midi_ready = True

    def stop(self):
        """Stop the Serial MIDI bridge and clean up resources."""
        self.thread_running = False
        self.midi_ready = False
        logging.info("Stopping threads...")

        # Wait for threads to finish using the instance variables
        if hasattr(self, 's_watcher') and self.s_watcher.is_alive():
            logging.debug("Joining serial watcher thread...")
            self.s_watcher.join()
            logging.debug("Serial watcher thread joined.")
        if hasattr(self, 's_writer') and self.s_writer.is_alive():
            logging.debug("Joining serial writer thread...")
            self.s_writer.join()
            logging.debug("Serial writer thread joined.")
        if hasattr(self, 'm_watcher') and self.m_watcher.is_alive():
            logging.debug("Joining midi watcher thread...")
            self.m_watcher.join()
            logging.debug("Midi watcher thread joined.")

        # Close the serial port
        if hasattr(self, 'ser') and self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("Serial port closed.")
        logging.info("Threads stopped.")

        # Update GUI LED color to indicate stopped state
        #self.gui.set_led_color("red")

def describe_midi_message(message):
    if not message or not isinstance(message, (list, tuple)):
        return str(message)
    status = message[0]
    channel = (status & 0x0F) + 1  # Channel for musicians (1-16)
    if status & 0xF0 == 176 and len(message) > 2:
        return f"Control Change: CC# {message[1]:<3} VALUE {message[2]:<3} CH {channel:<2}"
    elif status & 0xF0 == 144 and len(message) > 2:
        return f"Note On:   NOTE {message[1]:<3} VEL {message[2]:<3} CH {channel:<2}"
    elif status & 0xF0 == 128 and len(message) > 2:
        return f"Note Off:  NOTE {message[1]:<3} VEL {message[2]:<3} CH {channel:<2}"
    else:
        return f"Unknown MIDI: {message}"

class SerialMIDIApp(QtWidgets.QWidget):
    def toggle_serial_midi(self):
        if self.serial_midi is None:
            # Start the Serial MIDI bridge
            serial_port_name = self.port_dropdown.currentText()
            baud_rate = int(self.baud_dropdown.currentText())
            midi_in_name = self.midi_in_dropdown.currentText()
            midi_out_name = self.midi_out_dropdown.currentText()

            if midi_in_name == "Not Connected":
                midi_in_name = None
            if midi_out_name == "Not Connected":
                midi_out_name = None

            self.serial_midi = serialmidi.SerialMIDI(
                gui=self,
                serial_port_name=serial_port_name,
                serial_baud=baud_rate,
                midi_in_name=midi_in_name,
                midi_out_name=midi_out_name,
            )

            threading.Thread(target=self.serial_midi.start).start()
            self.toggle_button.setText("STOP")
        else:
            # Stop the Serial MIDI bridge
            self.serial_midi.stop()
            self.serial_midi = None
            self.toggle_button.setText("START")
