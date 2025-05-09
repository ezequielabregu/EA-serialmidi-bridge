// Compatible with Arduino boards that have the ATmega32U4 microcontroller
#include <MIDI.h>

// Pro Micro / Leonardo: use Serial_ type for USB virtual serial
MIDI_CREATE_INSTANCE(Serial_, Serial, MIDI);

void setup() {
  Serial.begin(115200);
  MIDI.begin(MIDI_CHANNEL_OMNI);
}

void loop() {
  MIDI.sendNoteOn(60, 100, 1);
  delay(250);
  MIDI.sendNoteOff(60, 0, 1);
  delay(250);
}
