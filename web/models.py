# coding: utf-8
# from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String, Table
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base

from web import db
import json


# Base = declarative_base()
# metadata = Base.metadata


class Tip(db.Model):
    __tablename__ = 'tips'

    tip_id = db.Column(db.String(50), primary_key=True)
    canonicalUrl = db.Column(db.String(300))
    likes = db.Column(db.Integer)
    likes_content = db.Column(db.String(2000))
    text = db.Column(db.String(2000))
    user_id = db.Column(db.ForeignKey(u'users.user_id'), index=True)
    venue_id = db.Column(db.ForeignKey(u'venues.venue_id'), index=True)
    ph = db.Column(db.String(1000))
    neg = db.Column(db.Float(asdecimal=True))
    neutral = db.Column(db.Float(asdecimal=True))
    pos = db.Column(db.Float(asdecimal=True))
    label = db.Column(db.String(45))
    ph2 = db.Column(db.Float())

    user = db.relationship(u'User', backref='tips')
    venue = db.relationship(u'Venue', backref='tips')
    # users = db.relationship(u'User', secondary='user_likes_tips')

    def __repr__(self):
        return '<Tip %s>' % self.tip_id

    def as_dict(self):
        tip_dict = {}
        tip_dict['tip_id'] = self.tip_id
        tip_dict['likes'] = self.likes
        tip_dict['likes_content'] = json.loads(self.likes_content)
        tip_dict['text'] = self.text
        tip_dict['user'] = self.user.as_dict()
        tip_dict['ph'] = self.ph
        return tip_dict


# t_user_likes_tips = Table(
#     'user_likes_tips', metadata,
#     Column('user_id', ForeignKey(u'users.user_id'),
#             nullable=False, index=True),
#     Column('tip_id', ForeignKey(u'tips.tip_id'), nullable=False, index=True),
#     Index('unique_user_likes_tip', 'user_id', 'tip_id', unique=True)
# )


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(50), primary_key=True)
    firstname = db.Column(db.String(45))
    gender = db.Column(db.String(45))
    photo = db.Column(db.String(200))
    lastname = db.Column(db.String(45))
    homecity = db.Column(db.String(100))
    complete_profile = db.Column(db.String(40000))
    region = db.Column(db.String(45))

    def __repr__(self):
        return '<User %s-%s %s>' % (self.user_id, self.firstname,
                                    self.lastname)

    def as_dict(self):
        user_dict = {}
        user_dict['user_id'] = self.user_id
        user_dict['firstname'] = self.firstname
        user_dict['gender'] = self.gender
        user_dict['photo'] = json.loads(self.photo)
        user_dict['lastname'] = self.lastname
        user_dict['homecity'] = self.homecity
        user_dict['region'] = self.region
        return user_dict


class Venue(db.Model):
    __tablename__ = 'venues'

    venue_id = db.Column(db.String(60), primary_key=True)
    name = db.Column(db.String(45))
    location = db.Column(db.String(1000))
    menu = db.Column(db.String(1000))
    stats = db.Column(db.String(1000))
    categories = db.Column(db.String(1000))

    def __repr__(self):
        return '<Venue %s>' % (self.venue_id)
