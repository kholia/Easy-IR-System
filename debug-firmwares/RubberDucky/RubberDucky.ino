#include "DigiKeyboard.h"

void setup() {
  // don't need to set anything up to use DigiKeyboard
  DigiKeyboard.delay(1000);

  DigiKeyboard.sendKeyStroke(0);
  DigiKeyboard.sendKeyStroke(0);
  DigiKeyboard.sendKeyStroke(0);
  DigiKeyboard.sendKeyStroke(0);
  DigiKeyboard.sendKeyStroke(0);
}


void loop() {
  // this is generally not necessary but with some older systems it seems to
  // prevent missing the first character after a delay:
  DigiKeyboard.sendKeyStroke(0);

  // Type out this string letter by letter on the computer (assumes US-style
  // keyboard)
  DigiKeyboard.println("I am hacking your computer!");

  // It's better to use DigiKeyboard.delay() over the regular Arduino delay()
  // if doing keyboard stuff because it keeps talking to the computer to make
  // sure the computer knows the keyboard is alive and connected
  DigiKeyboard.delay(1000);
}
