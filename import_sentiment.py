from web import db, models
from textblob import TextBlob

tips = models.Tip.query.all()

for tip in tips:
    try:
        tip_blob = TextBlob(tip.text)
        tip.ph2 = tip_blob.sentiment.polarity
        db.session.add(tip)
        print tip.tip_id + " successfully add to db session"
    except:
        print tip.tip_id + " failed to add to db session"

try:
    print 'commiting change'
    db.session.commit()
    print 'commit success'
except:
    print 'commit failed'
