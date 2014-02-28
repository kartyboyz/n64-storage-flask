
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.dialects.postgresql import ARRAY

import datetime

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    video_url = db.Column(db.VARCHAR(length=1024))
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

    video_url = db.Column(db.VARCHAR(length=1024))
    race_number = db.Column(db.Integer)

    characters = db.Column(ARRAY(db.VARCHAR(length=16)))
    course = db.Column(db.VARCHAR(length=32))

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


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'))
    race = db.relationship('Race', backref=db.backref('events'))

    event_number = db.Column(db.Integer)

    player = db.Column(db.Integer)
    timestamp = db.Column(db.Numeric(7, 1))
    lap = db.Column(db.Integer)

    event_type = db.Column(db.Enum("Lap", "Item", "Collision", "Pass", "Shortcut", "Tag", name='event_type'))
    event_subtype = db.Column(db.String)
    event_info = db.Column(db.String)

    linked_event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    linked_event = db.relationship('Event', backref=db.backref('linked_from', remote_side=id))

    image_url = db.Column(db.VARCHAR(length=1024))

    def __init__(self, race):
        self.race = race

