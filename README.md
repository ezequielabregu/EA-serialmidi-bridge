# EA Serial MIDI Bridge

*EA Serial MIDI Bridge* allows users to connect serial devices to MIDI applications, enabling seamless communication between hardware and software. It provides a graphical user interface (GUI) for easy configuration and monitoring of MIDI connections. You can use it to send and receive MIDI messages over a serial connection, making it ideal for musicians, developers, and hobbyists working with MIDI devices.

It works with any serial device that can send and receive MIDI messages, such as Arduino boards, ESP32, Raspberry Pi Pico, and other microcontrollers.

---

<div align="center">
  <img src="src/assets/EA-Bridge.gif" alt="Project Demo" width="400"/>
</div>

---

## Download

You can download the latest pre-built versions (`MacOS & Windows`) from the [`Releases page`](https://github.com/ezequielabregu/EA-serialmidi-bridge/releases).

---

## Features

- **Serial to MIDI Bridge**: Convert serial data to MIDI messages and vice versa.
- **User-Friendly GUI**: Intuitive interface for configuring and monitoring connections.
- **Real-Time Monitoring**: View incoming and outgoing MIDI messages in real-time.
- **Customizable Settings**: Adjust serial port settings, MIDI channels, and message formats.
- **Cross-Platform**: Compatible with Windows, macOS, and Linux.

---

## Project Structure

```plaintext
serialmidi-gui-app
├── src
│   ├── serialmidi.py        # Main logic for the Serial MIDI bridge
│   ├── gui.py               # GUI implementation using PyQt/PySide
│   └── assets
│       └── styles.qss       # Stylesheet for customizing the GUI appearance
├── requirements.txt         # List of dependencies
├── setup.py                 # Packaging configuration
└── README.md                # Project documentation
```

---

## Configuration

Below is a summary of the main configuration options available in the GUI:

| Option                | Description                                             |
|-----------------------|---------------------------------------------------------|
| Serial Port           | Select the serial device to connect to                  |
| Baud Rate             | Set the baud rate for serial communication              |
| MIDI Input Port       | Choose MIDI IN device or "Not Connected"                |
| MIDI Output Port      | Choose MIDI OUT device or "Not Connected"               |
| Debug Mode            | Toggle real-time debug output of MIDI messages          |
| LED Monitor           | Visual feedback for incoming/outgoing data              |

---
## Getting Started

Follow these steps to set up a virtual MIDI port and connect your Arduino to a DAW using EA Serial MIDI Bridge.

### Install a Virtual MIDI Port

#### **On macOS (IAC Driver)**

1. Open **Audio MIDI Setup** (found in Applications > Utilities).
2. Go to **Window > Show MIDI Studio**.
3. Double-click the **IAC Driver** icon.
4. In the IAC Driver window, check **"Device is online"**.
5. (Optional) Click the **"+"** button to add more virtual ports if needed.
6. Close the window. The IAC Driver port is now available for MIDI routing.

#### **On Windows (loopMIDI by Tobias Erichsen)**

1. Download and install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html).
2. Launch **loopMIDI**.
3. Click the **"+"** button to create a new virtual MIDI port (e.g., "loopMIDI Port").
4. Leave loopMIDI running in the background.

---

### Connect Your Devices

#### **Hardware and Software Setup**

1. Plug in your Arduino (or other serial MIDI device) via USB.
2. Launch **EA Serial MIDI Bridge**.
3. In the app, select your Arduino's serial port and the virtual MIDI port (IAC Driver or loopMIDI) for MIDI IN/OUT as needed.
4. Open your DAW (Ableton, Logic, FL Studio, etc.).
5. In your DAW's MIDI settings, select the same virtual MIDI port for input and/or output.

---

### 3. Example Connection Diagram

```plaintext
+-----------+         USB         +---------------------+        Virtual MIDI       +--------+
|  Arduino  | <-----------------> | EA Serial MIDI      | <-----------------------> |  DAW   |
|  (Serial) |                     |    Bridge App       |   (IAC Driver/loopMIDI)   |        |
+-----------+                     +---------------------+                           +--------+
```

---

## Contributing

Contributions are welcome! If you would like to contribute to this project, please fork the repository and create a pull request.
I appreciate any improvements, bug fixes, or new features you can provide. Before submitting a pull request, please ensure that your code adheres to the project's coding standards and passes all tests.

Bug reports and feature requests are also welcome via [GitHub Issues](https://github.com/ezequielabregu/EA-serialmidi-bridge/issues).

## Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage

To run the application, execute the following command:

```bash
python src/gui.py
```

Make sure to have your MIDI devices connected and specify the correct serial port in the GUI settings.

## Dependencies

This project requires the following Python packages:

- PyQt6 (for GUI)
- python-rtmidi (for MIDI handling)
- pyserial (for serial communication)
- pyinstaller (for packaging, optional)

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## References

This app is based on the [**serialmidi**](https://github.com/raspy135/serialmidi) repository, which provides a user-friendly way convert serial data to MIDI messages and vice versa.
