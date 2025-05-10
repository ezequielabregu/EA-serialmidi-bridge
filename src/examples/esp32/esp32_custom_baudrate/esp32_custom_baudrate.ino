#include <MIDI.h>

// 1. Define a structure to configure the custom baud rate
struct HairlessMidiSettings : public MIDI_NAMESPACE::DefaultSerialSettings {
  static const long BaudRate = 115200; // Sets the baud rate
};

// 2. Create a custom MIDI instance using your settings
// For ESP32, 'Serial' is generally UART0 (connected to USB)
// and the HardwareSerial class is correct for the ESP32's UARTs.
MIDI_CREATE_CUSTOM_INSTANCE(HardwareSerial, Serial, MIDI, HairlessMidiSettings);


void setup() {
  // You don't need to call Serial.begin(115200) explicitly here,
  // as MIDI.begin() will use the HairlessMidiSettings configuration.
  // If you include it, make sure it matches the baud rate defined above.
  // Serial.begin(115200); // If you wish, but MIDI.begin() will already do it

  MIDI.begin(MIDI_CHANNEL_OMNI); // This will use BaudRate = 115200 from HairlessMidiSettings
}

void loop() {
  MIDI.sendNoteOn(60, 100, 1);
  delay(250);
  MIDI.sendNoteOff(60, 0, 1);
  delay(250);
}