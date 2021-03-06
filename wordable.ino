#include <Arduboy2.h>

#include "output.h"

int ptr = 0;

Arduboy2 arduboy;

void setup() {
  arduboy.begin();
  arduboy.setFrameRate(30);
}

void loop() {
  if (!(arduboy.nextFrame())) return;

  arduboy.clear();
  arduboy.print("Hello World");
  arduboy.print(wordlist1[ptr]);
  arduboy.print(wordlist2[ptr]);
  arduboy.display();

  ptr += 1;
  
  return;    
}
