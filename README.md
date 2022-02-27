# wordable
Wordle for the Arduboy

Wordle by Josh Wardle made a big spash on the internet in the end of 2021. It is a very simple game that I wanted to port to the Arduboy.  
The challege is to access the ~13000 5-letter word dictionary only using the Arduboy's 32KB of program memory. 
It would be trivial to store the words with an additional flash chip, like the Arduboy FX, but I wanted to see if the original could handle it.
The word list is broken up into ~2000 solution words and an addition ~11000 legal guesses.
A quick calculation shows that storing a letter per byte for all the 5-letter words would be > 64KB, so some kind of compression is needed.

One approach would be to use a Bloom filter, which ideally would use ~10 bits per entry but could be less. 
A Bloom filter works by having one or more hash functions to producing an index an array of bits.  Generally 1-3 hash functions are used.  
If the bit at each index of the hash functions for a given entry is 1, then the entry is determined to be in the set. 
At 10 bits per word, ~16KB would be needed or 1/2 of the Adruboy program size. 
But this approach has a couple of disadvantages:
1) Can have false positives, which isn't a big deal but can make the game easier as some gibberish word will be considered valid
2) Will need to store the ~2000 solution word separately since the Bloom filter can only say if the word is part of the dictionary, but not what the word is.

So, I looked into using a Trie data structure to compress the word-list, where all common prefixes for a set of word is only stored once.
In addition, frequency analysis of the letter can be used with a variable-bit encoding to allow the most frequent letter to be stored in fewer bits.

By combining these techniques, I was able to store the word-list using ~2 bits per letter, for a total of ~16KB. 
The disadvantage is that the way the dictionary is stored, it can only read serially. 
This doesn't seem too bad since the Arduboy has a relatively fast processor, and the dictionary only needs to be accessed a few times while playing the game.
