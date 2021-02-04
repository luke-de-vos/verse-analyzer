# verse-analyzer

rhymeClass.py discerns meaningful rhymes and assonance in the context of rap lyrics.

## Background

Determining whether or not two words rhyme is easily accomplished by comparing their phonetic spelling.

Determining if that rhyme is intentional and impactful in the context of rap lyrics is a far more complex task.

Skillful rappers are masters of rhythm and enunciation. They leverage these skills in their performance to selectively emphasize the harmonious aspects of words or phrases they intend to rhyme. As a result, these words may sound like rhymes as perfect as 'greenery' and 'scenery', when they actually only share a few vowel sounds. Take, for example, the following phrases:
* arms are heavy
* mom's spaghetti
* on forgetting

Despite not rhyming in the traditional sense, these arrangements of sounds have the sonic impact of rhymes when delivered by Eminem in his song "Lose Yourself". Thus, a program attempting to visualize a verse's rhymes by text alone must consider that vowel sounds alone may constitute a rhyme. However, flagging every syllable, word, or phrase that shares vowel sounds with another nearby yields an invalidating number of false positives.

**rhymeClass.py** goes through the following steps to generate more accurate assessments of rhymes than simple phonetics analysis:

* use NLTK to determine each word's part of speech
* divide each word into its syllables
* mark each syllable as emphasized or unemphasized
** one syllable words are initially all emphasized. Then, **rhymeClass.py** estimates the emphasis of each one syllable word based on its part of speech, position in sentence, and the emphasis of adjacent syllables.
* flag emphasized words within 12 syllables of each other that traditionally rhyme
* flag unemphasized words if they are part of a string of emphasized rhymes
* color code accordingly

**rhymeClass.py** is a work in progress, and textual analysis of a spoken art form will always be limited. However, combined with some speech recognition and sensitivity to rhymth, I believe these strategies could approach human levels of rhyme-tagging accuracy.
