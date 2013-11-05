
from flask import Flask
from flask.ext.restful import Api, Resource, marshal, fields

from .models import Session, Race
from . import db, app

api = Api(app)


class SessionAPI(Resource):

    fields = {
        'id': fields.Integer,
        'date': fields.DateTime,
        'video_url': fields.String,
        'video_split': fields.Boolean,
    }

    def get(self, session_id):
        session = db.session.query(Session).filter(Session.id == session_id).first()
        return marshal(session, SessionAPI.fields), 200


    def put(self, session_id):
        pass


    def delete(self, session_id):
        session = db.session.query(Session).filter(Session.id == session_id).first()


class SessionListAPI(Resource):
    def get(self):
        sessions = db.session.query(Session)
        return {}, 200

    def post(self):
        pass


class RaceAPI(Resource):

    fields = {
        'id': fields.Integer,
        'session_id': fields.Integer,
        'race_number': fields.Integer,
        'video_url': fields.String
    }

    def get(self, race_id):
        race = db.session.query(Race).filter(Race.id == race_id).first()
        return marshal(race, RaceAPI.fields), 200

    def put(self, race_id):
        pass

    def delete(self, race_id):
        pass


class RaceListAPI(Resource):
    def get(self, session_id):
        pass

    def post(self, session_id):
        pass


api.add_resource(SessionListAPI, '/sessions')
api.add_resource(SessionAPI, '/sessions/<int:session_id>')
api.add_resource(RaceListAPI, '/sessions/<int:session_id>/races')
api.add_resource(RaceAPI, '/races/<int:race_id>')

