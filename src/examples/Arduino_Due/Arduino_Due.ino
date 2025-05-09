//not fully tested with Arduino Due

#include <MIDI.h>

MIDI_CREATE_INSTANCE(UARTClass, Serial, MIDI);

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
