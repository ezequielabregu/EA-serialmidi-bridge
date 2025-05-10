#include <MIDI.h>

MIDI_CREATE_INSTANCE(HardwareSerial, Serial, MIDI);

void setup() {
  Serial.begin(31250); //baudrate
  MIDI.begin(MIDI_CHANNEL_OMNI); 
}

void loop() {
  MIDI.sendNoteOn(60, 100, 1);
  delay(250);
  MIDI.sendNoteOff(60, 0, 1);
  delay(250);
}