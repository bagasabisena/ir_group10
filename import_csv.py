from web import db, models
from textblob import TextBlob
import csv

# create csv to manually label

tips = models.Tip.query.all()

f = open('food2.csv', 'wt')
try:
    writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(('sentence', 'tip_id'))
    for tip in tips:
        tip_blob = TextBlob(tip.text)
        for sentence in tip_blob.sentences:
            writer.writerow((sentence, tip.tip_id))
finally:
    f.close()
