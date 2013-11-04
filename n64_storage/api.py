
from flask import Flask
from flask.ext.restful import Api, Resource, marshal, fields

from .models import Session, Race
from . import db

api = Api()


class SessionResource(Resource):

    fields = {
        'id': fields.Integer,
        'date': fields.DateTime,
        'video_url': fields.String,
        'video_split': fields.Boolean,
        'races_url': fields.Url('raceresource')
    }

    def get(self, session_id):
        session = db.session.query(Session).filter(Session.id == session_id)
        return marshal(session, fields), 200


    def put(self, session_id):
        pass

    def delete(self, session_id):
        session = db.session.query(Session).filter(Session.id == session_id)


class SessionListResource(Resource):
    def get(self):
        sessions = db.session.query(Session)

    def post(self):
        pass


class RaceResource(Resource):
    def get(self, race_id):
        pass

    def put(self, race_id):
        pass

    def delete(self, race_id):
        pass


class RaceListResource(Resource):
    def get(self, session_id):
        pass

    def post(self, session_id):
        pass


api.add_resource(SessionListResource, '/sessions')
api.add_resource(SessionResource, '/sessions/<int:session_id>')
api.add_resource(RaceListResource, '/sessions/<int:session_id>/races')
api.add_resource(RaceResource, '/races/<int:race_id>')
