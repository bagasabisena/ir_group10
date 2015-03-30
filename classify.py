from web import db, models
from textblob import TextBlob
import csv

# create csv to manually label

tips = models.Tip.query.all()

data = []

f = open('food2.csv', 'rb')
try:
    reader = csv.reader(f, dialect="excel")
    for r in reader:
        data.append(r)
finally:
    f.close()
