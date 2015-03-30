from textblob import Word
from textblob.wordnet import NOUN


word = Word('chicken')

synsets = word.get_synsets(pos=NOUN)
for s in synsets:
    print s.hypernyms()
