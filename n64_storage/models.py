
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import datetime

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)


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

    start_time = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    video_split = db.Column(db.Boolean)

    def __init__(self, session, start_time=0, duration=0):
        self.session = session
        self.start_time = start_time
        self.duration = duration
        self.video_url = ''
        self.race_number = 0

    def __repr__(self):
        return "Race(%r, %r, %r)" % (self.session, self.video_url, self.race_number)

