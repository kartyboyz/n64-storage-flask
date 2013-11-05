
from flask import Flask
from flask import request
from flask.ext.restful import Api, Resource, marshal, fields, abort

from .models import Session, Race, db


class SessionAPI(Resource):

    fields = {
        'id': fields.Integer,
        'date': fields.DateTime,
        'video_url': fields.String,
        'video_split': fields.Boolean,
    }
    allowed_updates = ['video_url']


    def get(self, session_id):
        session = Session.query.get_or_404(session_id)
        return marshal(session, SessionAPI.fields), 200


    def put(self, session_id):
        data = request.get_json()

        session = Session.query.get_or_404(session_id)

        for key, value in data.items():
            if key in SessionAPI.allowed_updates:
                session.__setattr__(key, value)

        db.session.add(session)
        db.session.commit()

        return {"message": "Success"}


    def delete(self, session_id):
        session = Session.query.get_or_404(session_id)
        db.session.delete(session)
        db.session.commit()
        return {"message": "Success"}


class SessionListAPI(Resource):
    def get(self):
        sessions = db.session.query(Session).all()
        l = [marshal(s, SessionAPI.fields) for s in sessions]
        return l


    def post(self):
        if request.content_type != 'application/json':      
            abort(400, message="Invalid Content-Type")                                       

        data = request.get_json()
        if not isinstance(data, dict):
            data = {}

        url = data.get('video_url', '')
        s = Session(url)

        db.session.add(s)
        db.session.commit()

        return {"message": "Success", "id": s.id}


class RaceAPI(Resource):

    fields = {
        'id': fields.Integer,
        'session_id': fields.Integer,
        'race_number': fields.Integer,
        'video_url': fields.String
    }
    allowed_updates = ['video_url', 'start_time', 'duration']


    def get(self, race_id):
        race = Race.query.get_or_404(race_id)
        return marshal(race, RaceAPI.fields), 200


    def put(self, race_id):
        data = request.get_json()

        race = Race.query.get_or_404(race_id)

        for key, value in data.items():
            if key in RaceAPI.allowed_updates:
                race.__setattr__(key, value)

        db.session.add(race)
        db.session.commit()

        return {"message": "Success"}


    def delete(self, race_id):
        race = Race.query.get_or_404(race_id)
        db.session.delete(race)
        db.session.commit()
        return {'message': "Success"}


class RaceListAPI(Resource):

    required_fields = ['start_time', 'duration']

    def get(self, session_id):
        session = Session.query.get_or_404(session_id)
        if session is None:
            abort(404, message="Session {} doesn't exist".format(session_id))

        l = [marshal(r, RaceAPI.fields) for r in session.races]
        return l


    def post(self, session_id):
        if request.content_type != 'application/json':      
            abort(400, message="Invalid Content-Type")                                       

        session = Session.query.get_or_404(session_id)

        data = request.get_json()
        if not isinstance(data, dict):
            data = {}

        for item in RaceListAPI.required_fields:
            if not item in data:
                abort(400, message="Incomplete Request")

        race_number = Race.query.filter(Race.session_id == session_id).count() + 1

        race = Race(session)
        
        for item in RaceListAPI.required_fields:
            race.__setattr__(item, data[item])

        race.race_number = race_number

        db.session.add(race)
        db.session.commit()

        return {'message': "Success", 'id':race.id}




def configure_resources(api):
    api.add_resource(SessionListAPI, '/sessions')
    api.add_resource(SessionAPI, '/sessions/<int:session_id>')
    api.add_resource(RaceListAPI, '/sessions/<int:session_id>/races')
    api.add_resource(RaceAPI, '/races/<int:race_id>')

