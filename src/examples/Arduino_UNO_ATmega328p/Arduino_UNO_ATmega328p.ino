// Compatible with Arduino boards that have the ATmega328P microcontroller.
#include <MIDI.h>

MIDI_CREATE_DEFAULT_INSTANCE();

void setup() {
  MIDI.begin(MIDI_CHANNEL_OMNI);
  Serial.begin(115200); // USB serial
}

void loop() {
  MIDI.sendNoteOn(60, 100, 1);
  delay(250);
  MIDI.sendNoteOff(60, 0, 1);
  delay(250);
}
