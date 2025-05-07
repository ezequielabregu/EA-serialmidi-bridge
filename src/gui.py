import sys
import threading
import logging
import serialmidi
import os
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt, pyqtSignal
from serial.tools import list_ports
import rtmidi


class SerialMIDIApp(QtWidgets.QWidget):
    log_signal = pyqtSignal(str)
    led_blink_signal = pyqtSignal(str)
    midi_in_led_blink_signal = QtCore.pyqtSignal(str)
    midi_out_led_blink_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Create LED and Refresh button before initUI
        self.led_label = QtWidgets.QLabel()
        #self.set_led_color("gray")
        self.led_label.setFixedSize(16, 16)
        self.led_label.setStyleSheet("background: #444; border-radius: 7px;")

        self.refresh_button = QtWidgets.QPushButton("Refresh Ports")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.refresh_serial_ports)

        self.initUI()
        self.serial_midi = None
        self.log_signal.connect(self.log_message)
        self.led_blink_signal.connect(self.blink_led)
        self.midi_in_led_blink_signal.connect(self.blink_midi_in_led)
        self.midi_out_led_blink_signal.connect(self.blink_midi_out_led)

        # Set up logging handler ONCE here
        logging.getLogger().handlers.clear()
        logging.getLogger().addHandler(GuiLogHandler(self))
        # Set initial level based on checkbox
        self.update_logging_level()

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

        port_layout = QtWidgets.QHBoxLayout()
        port_layout.setSpacing(0) 
        port_layout.addWidget(self.led_label)       # 0. LED (leftmost)
        port_layout.addWidget(self.port_label)      # 1. Serial Port label
        #port_layout.addWidget(self.led_label)       # 2. LED (immediately right of label)
        port_layout.addSpacing(160) 
        port_layout.addWidget(self.refresh_button)  # 3. Refresh button (rightmost)

        layout.addLayout(port_layout)

        self.port_dropdown = QtWidgets.QComboBox()
        self.refresh_serial_ports()
        layout.addWidget(self.port_dropdown)

        # MIDI Out Port Selection
        self.midi_out_label = QtWidgets.QLabel("MIDI Out")
        self.midi_out_led = QtWidgets.QLabel()
        self.midi_out_led.setFixedSize(16, 16)
        self.midi_out_led.setStyleSheet("background: #444; border-radius: 7px;")
        out_layout = QtWidgets.QHBoxLayout()
        out_layout.setSpacing(0) 
        out_layout.addWidget(self.midi_out_led)
        out_layout.addWidget(self.midi_out_label)
        out_layout.addStretch()
        layout.addLayout(out_layout)

        self.midi_out_dropdown = QtWidgets.QComboBox()
        self.midi_out_dropdown.addItem("Not Connected")
        layout.addWidget(self.midi_out_dropdown)

        # MIDI In Port Selection
        self.midi_in_label = QtWidgets.QLabel("MIDI In")
        self.midi_in_led = QtWidgets.QLabel()
        self.midi_in_led.setFixedSize(16, 16)
        self.midi_in_led.setStyleSheet("background: #444; border-radius: 7px;")
        in_layout = QtWidgets.QHBoxLayout()
        in_layout.setSpacing(0) 
        in_layout.addWidget(self.midi_in_led)
        in_layout.addWidget(self.midi_in_label)
        in_layout.addStretch()
        layout.addLayout(in_layout)

        self.midi_in_dropdown = QtWidgets.QComboBox()
        self.midi_in_dropdown.addItem("Not Connected")
        layout.addWidget(self.midi_in_dropdown)

        # Refresh MIDI Ports after defining the dropdowns
        self.refresh_midi_ports()

        # Baud Rate Input
        self.baud_label = QtWidgets.QLabel("Baud Rate")
        layout.addWidget(self.baud_label)

        self.baud_dropdown = QtWidgets.QComboBox()
        self.baud_dropdown.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_dropdown.setCurrentText("115200")  # Set default value
        layout.addWidget(self.baud_dropdown)

        # Debug Checkbox
        layout.addSpacing(12)  
        self.debug_checkbox = QtWidgets.QCheckBox("Debug")
        self.debug_checkbox.stateChanged.connect(self.update_logging_level)
        layout.addWidget(self.debug_checkbox)
        layout.addSpacing(12) 
        # Toggle Button
        self.toggle_button = QtWidgets.QPushButton("START")
        #self.toggle_button.setFixedHeight(32)  # or whatever looks good
        self.toggle_button.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.toggle_button.clicked.connect(self.toggle_serial_midi)
        layout.addWidget(self.toggle_button)

        layout.addSpacing(8) 
        
        # Debugging Text Box
        self.debug_text_box = QtWidgets.QTextEdit()
        self.debug_text_box.setReadOnly(True)
        self.debug_text_box.setPlaceholderText("Debug output will appear here...")
        layout.addWidget(self.debug_text_box)

        self.setLayout(layout)

    def log_message(self, message):
        """Log a message to the debugging text box and ensure it scrolls to the bottom."""
        self.debug_text_box.append(message)
        self.debug_text_box.moveCursor(QTextCursor.MoveOperation.End)

    def blink_led(self, color):
        self.set_led_color(color)
        QtCore.QTimer.singleShot(100, lambda: self.set_led_color("gray"))

    def blink_midi_in_led(self, color):
        self.midi_in_led.setStyleSheet(f"background: {color}; border-radius: 8px;")
        QtCore.QTimer.singleShot(100, lambda: self.midi_in_led.setStyleSheet("background: #444; border-radius: 8px;"))

    def blink_midi_out_led(self, color):
        self.midi_out_led.setStyleSheet(f"background: {color}; border-radius: 8px;")
        QtCore.QTimer.singleShot(100, lambda: self.midi_out_led.setStyleSheet("background: #444; border-radius: 8px;"))

    def refresh_serial_ports(self):
        """Refresh the list of available serial ports."""
        self.port_dropdown.clear()
        ports = list_ports.comports()
        for port in ports:
            self.port_dropdown.addItem(port.device)

    def refresh_midi_ports(self):
        midi_out = rtmidi.MidiOut()
        midi_in = rtmidi.MidiIn()

        # Populate MIDI Out dropdown
        current_out = self.midi_out_dropdown.currentText()
        self.midi_out_dropdown.clear()
        self.midi_out_dropdown.addItem("Not Connected")
        for port in midi_out.get_ports():
            self.midi_out_dropdown.addItem(port)
        if current_out in [self.midi_out_dropdown.itemText(i) for i in range(self.midi_out_dropdown.count())]:
            self.midi_out_dropdown.setCurrentText(current_out)

        # Populate MIDI In dropdown
        current_in = self.midi_in_dropdown.currentText()
        self.midi_in_dropdown.clear()
        self.midi_in_dropdown.addItem("Not Connected")
        for port in midi_in.get_ports():
            self.midi_in_dropdown.addItem(port)
        if current_in in [self.midi_in_dropdown.itemText(i) for i in range(self.midi_in_dropdown.count())]:
            self.midi_in_dropdown.setCurrentText(current_in)

    def toggle_serial_midi(self):
        """Toggle the Serial MIDI bridge between Start and Stop."""
        if self.serial_midi is None:
            # Start the Serial MIDI bridge
            serial_port_name = self.port_dropdown.currentText()
            baud_rate = int(self.baud_dropdown.currentText())
            midi_in_name = self.midi_in_dropdown.currentText()
            print("Selected MIDI In Port:", midi_in_name)
            midi_out_name = self.midi_out_dropdown.currentText()

            # Update level based on checkbox
            self.update_logging_level()

            self.serial_midi = serialmidi.SerialMIDI(
                gui=self,
                serial_port_name=serial_port_name,
                serial_baud=baud_rate,
                midi_in_name=midi_in_name,
                midi_out_name=midi_out_name,
            )

            threading.Thread(target=self.serial_midi.start).start()

            self.toggle_button.setText("STOP")
            #self.toggle_button.setStyleSheet("background-color: #2980b9; color: white;")
            self.toggle_button.setProperty("active", True)
            self.toggle_button.style().unpolish(self.toggle_button)
            self.toggle_button.style().polish(self.toggle_button)
            logging.info("Serial MIDI Bridge started.")
        else:
            # Stop the Serial MIDI bridge
            self.serial_midi.stop()
            self.serial_midi = None

            self.toggle_button.setText("START")
            #self.toggle_button.setStyleSheet("")  # Reset to default
            self.toggle_button.setProperty("active", False)
            self.toggle_button.style().unpolish(self.toggle_button)
            self.toggle_button.style().polish(self.toggle_button)
            logging.info("Serial MIDI Bridge stopped.")

    def update_logging_level(self):
        if self.debug_checkbox.isChecked():
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)

    def set_led_color(self, color):
        pixmap = QtGui.QPixmap(14, 14)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 14, 14)
        painter.end()
        self.led_label.setPixmap(pixmap)


class GuiLogHandler(logging.Handler):
    """Custom logging handler to redirect logs to the GUI text box."""
    def __init__(self, gui):
        super().__init__()
        self.gui = gui

    def emit(self, record):
        log_entry = self.format(record)
        # Use the signal to update the GUI safely
        self.gui.log_signal.emit(log_entry)


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Load the stylesheet using an absolute path
    stylesheet_path = os.path.join(os.path.dirname(__file__), "assets", "styles.qss")
    with open(stylesheet_path, "r") as f:
        app.setStyleSheet(f.read())

    ex = SerialMIDIApp()
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
