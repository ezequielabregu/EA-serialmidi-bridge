import sys
import threading
import logging
import serialmidi
import os
from PyQt5 import QtWidgets, QtCore  # Import QtCore for QTimer
from PyQt5.QtGui import QTextCursor  # Import QTextCursor for text box scrolling
from serial.tools import list_ports
import rtmidi


class SerialMIDIApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.serial_midi = None

    def closeEvent(self, event):
        """Handle the window close event to clean up resources."""
        if self.serial_midi:
            self.serial_midi.stop()  # Stop the Serial MIDI bridge
            self.serial_midi = None
        logging.info("Application closed.")
        QtWidgets.QApplication.quit()  # Ensure the application terminates completely
        event.accept()  # Ensure the window closes

    def initUI(self):
        self.setWindowTitle("EA Serial MIDI Bridge")
        self.setGeometry(100, 100, 400, 500)

        layout = QtWidgets.QVBoxLayout()

        # Serial Port Selection
        self.port_label = QtWidgets.QLabel("Serial Port")

        # Create a horizontal layout for the label and refresh button
        port_layout = QtWidgets.QHBoxLayout()
        port_layout.addWidget(self.port_label)

        self.refresh_button = QtWidgets.QPushButton("Refresh Ports")
        self.refresh_button.setObjectName("refreshButton")  # Set object name for styling
        self.refresh_button.clicked.connect(self.refresh_serial_ports)
        port_layout.addWidget(self.refresh_button)

        layout.addLayout(port_layout)  # Add the horizontal layout to the main layout

        self.port_dropdown = QtWidgets.QComboBox()
        self.refresh_serial_ports()
        layout.addWidget(self.port_dropdown)

        # Baud Rate Input
        self.baud_label = QtWidgets.QLabel("Baud Rate")
        layout.addWidget(self.baud_label)

        self.baud_dropdown = QtWidgets.QComboBox()
        self.baud_dropdown.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_dropdown.setCurrentText("115200")  # Set default value
        layout.addWidget(self.baud_dropdown)

        # MIDI Out Port Selection
        self.midi_out_label = QtWidgets.QLabel("MIDI Out Port:")
        layout.addWidget(self.midi_out_label)

        self.midi_out_dropdown = QtWidgets.QComboBox()
        layout.addWidget(self.midi_out_dropdown)

        # MIDI In Port Selection
        self.midi_in_label = QtWidgets.QLabel("MIDI In Port:")
        layout.addWidget(self.midi_in_label)

        self.midi_in_dropdown = QtWidgets.QComboBox()
        layout.addWidget(self.midi_in_dropdown)

        # Refresh MIDI Ports after defining the dropdowns
        self.refresh_midi_ports()

        # Debug Checkbox
        self.debug_checkbox = QtWidgets.QCheckBox("Enable Debug")
        layout.addWidget(self.debug_checkbox)

        # Toggle Button
        self.toggle_button = QtWidgets.QPushButton("START")
        self.toggle_button.clicked.connect(self.toggle_serial_midi)
        layout.addWidget(self.toggle_button)

        # Debugging Text Box
        self.debug_text_box = QtWidgets.QTextEdit()
        self.debug_text_box.setReadOnly(True)
        layout.addWidget(self.debug_text_box)

        self.setLayout(layout)

    def log_message(self, message):
        """Log a message to the debugging text box and ensure it scrolls to the bottom."""
        self.debug_text_box.append(message)
        self.debug_text_box.moveCursor(QTextCursor.End)  # Use QTextCursor from QtGui

    def refresh_serial_ports(self):
        """Refresh the list of available serial ports."""
        self.port_dropdown.clear()
        ports = list_ports.comports()
        for port in ports:
            self.port_dropdown.addItem(port.device)

    def refresh_midi_ports(self):
        """Refresh the list of available MIDI ports."""
        midi_out = rtmidi.MidiOut()  # Use MidiOut instead of RtMidiOut
        midi_in = rtmidi.MidiIn()    # Use MidiIn instead of RtMidiIn

        # Populate MIDI Out dropdown
        self.midi_out_dropdown.clear()
        for port in midi_out.get_ports():
            self.midi_out_dropdown.addItem(port)

        # Populate MIDI In dropdown
        self.midi_in_dropdown.clear()
        for port in midi_in.get_ports():
            self.midi_in_dropdown.addItem(port)

    def toggle_serial_midi(self):
        """Toggle the Serial MIDI bridge between Start and Stop."""
        if self.serial_midi is None:
            # Start the Serial MIDI bridge
            serial_port_name = self.port_dropdown.currentText()
            baud_rate = int(self.baud_dropdown.currentText())
            midi_in_name = self.midi_in_dropdown.currentText()
            midi_out_name = self.midi_out_dropdown.currentText()
            debug = self.debug_checkbox.isChecked()

            # Configure logging
            logging.getLogger().handlers.clear()  # Clear existing handlers
            if debug:
                logging.basicConfig(level=logging.DEBUG)
            else:
                logging.basicConfig(level=logging.INFO)

            self.serial_midi = serialmidi.SerialMIDI(
                gui=self,
                serial_port_name=serial_port_name,
                serial_baud=baud_rate,
                midi_in_name=midi_in_name,
                midi_out_name=midi_out_name,
            )

            # Redirect logging to the text box
            logging.getLogger().addHandler(GuiLogHandler(self))

            threading.Thread(target=self.serial_midi.start).start()

            self.toggle_button.setText("STOP")
            logging.info("Serial MIDI Bridge started.")
        else:
            # Stop the Serial MIDI bridge
            self.serial_midi.stop()  # Call the stop method to close the serial port
            self.serial_midi = None

            self.toggle_button.setText("START")
            logging.info("Serial MIDI Bridge stopped.")


class GuiLogHandler(logging.Handler):
    """Custom logging handler to redirect logs to the GUI text box."""
    def __init__(self, gui):
        super().__init__()
        self.gui = gui

    def emit(self, record):
        log_entry = self.format(record)
        self.gui.log_message(log_entry)


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Load the stylesheet using an absolute path
    stylesheet_path = os.path.join(os.path.dirname(__file__), "assets", "styles.qss")
    with open(stylesheet_path, "r") as f:
        app.setStyleSheet(f.read())

    ex = SerialMIDIApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()