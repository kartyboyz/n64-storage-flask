
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import datetime

from . import app, db


class Session(db.Model):
    """
    
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    video_url = db.Column(db.VARCHAR(length=100))
    video_split = db.Column(db.Boolean)

    def __init__(self, video_url='', date=None):
        self.date = date if date is not None else datetime.datetime.now()
        self.video_url = video_url
        self.video_split = False

    def __repr__(self):
        return 'Session(%r, %r)' % (self.video_url, self.date)


class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    session = db.relationship('Session', backref=db.backref('races'))
    video_url = db.Column(db.VARCHAR(length=100))
    race_number = db.Column(db.Integer)

    def __init__(self, session, video_url, race_number):
        self.session = session
        self.video_url = video_url
        self.race_number = race_number

    def __repr__(self):
        return "Race(%r, %r, %r)" % (self.session, self.video_url, self.race_number)

