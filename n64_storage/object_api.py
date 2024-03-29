
from flask import request
from flask.ext.restful import Resource, marshal, fields, abort

from boto.ec2 import autoscale
from boto import sqs
from boto.sqs.message import Message
import json


from .models import Session, Race, Event, db, ARRAY
from . import app
from . import video_api

from .query import EventQuery, LanguageDescription

def increment_asg(group_name):
    conn = autoscale.connect_to_region(app.config['AWS_REGION'])
    for group in conn.get_all_groups():
        if group.name == app.config['AUTOSCALE_GROUP']:
            break

    group.set_capacity(min(group.desired_capacity + 1, group.max_size))


class SessionAPI(Resource):

    fields = {
        'id': fields.Integer,
        'date': fields.DateTime,
        'owner': fields.String,
        'video_url': fields.String,
        'video_split': fields.Boolean,
    }
    allowed_updates = ['video_url', 'video_split', 'owner']


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
        owner = data.get('owner', '')
        s = Session(url)
        s.owner = owner

        db.session.add(s)
        db.session.commit()

        if app.config['SEND_MESSAGES']:
            msg = Message()
            msg.set_body(json.dumps(marshal(s, SessionAPI.fields)))
            app.session_queue.write(msg)

        increment_asg('video-processing-group')


        return {"message": "Success", "id": s.id}


class RaceAPI(Resource):

    fields = {
        'id': fields.Integer,
        'session_id': fields.Integer,
        'race_number': fields.Integer,
        'audio_url': fields.String,
        'video_url': fields.String,
        'video_processed_url': fields.String,
        'start_time' : fields.Integer,
        'duration' : fields.Integer,
        'characters': fields.List(fields.String),
        'player_regions' : fields.List(fields.List(fields.List(fields.Integer))),
        'course' : fields.String,
        'processed' : fields.Boolean,
        'video_split': fields.Boolean,
    }
    allowed_updates = ['video_url', 'start_time', 'duration', 'characters',
            'course', 'audio_url', 'player_regions', 'processed', 'video_split']


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


class AllRaceAPI(Resource):
    def get(self):
        l = [marshal(r, RaceAPI.fields) for r in Race.query.all()]
        return l

class RaceListAPI(Resource):

    required_fields = ['start_time', 'duration']
    optional_fields = ['video_url', 'characters', 'course',
            'player_regions', 'processed', 'video_split']

    def get(self, session_id):
        session = Session.query.get_or_404(session_id)
        if session is None:
            abort(404, message="Session {} doesn't exist".format(session_id))

        races = Race.query.filter(Race.session == session).order_by(Race.race_number)

        l = [marshal(r, RaceAPI.fields) for r in races]
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

        for item in RaceListAPI.optional_fields:
            if item in data:
                race.__setattr__(item, data[item])

        race.race_number = race_number

        video_api.submit_transcode_job(race)

        db.session.add(race)
        db.session.commit()

        if app.config['SEND_MESSAGES']:
            msg = Message()
            msg.set_body(json.dumps(marshal(race, RaceAPI.fields)))
            app.race_queue.write(msg)

        return {'message': "Success", 'id':race.id}


class EventAPI(Resource):

    fields = {
        'id'             : fields.Integer,
        'race_id'        : fields.Integer,
        'player'         : fields.Integer,
        'place'          : fields.Integer,
        'lap'            : fields.Integer,
        'timestamp'      : fields.Fixed(1),
        'image_url'      : fields.String,
        'event_type'     : fields.String,
        'event_subtype'  : fields.String,
        'event_info'     : fields.String,
        'linked_event_id': fields.Integer,
    }

    def get(self, event_id):
        event = Race.query.get_or_404(event_id)
        return marshal(event, EventAPI.fields), 200

    def delete(self, event_id):
            event = Event.query.get_or_404(event_id)
            db.session.delete(event)
            db.session.commit()
            return {'message': "Success"}


class EventListAPI(Resource):

    required_fields = ['timestamp', 'event_type', 'event_subtype']
    optional_fields = ['player', 'lap', 'image_url', 'event_info',
            'linked_event_id', 'place']

    def get(self, race_id):
        race = Race.query.get_or_404(race_id)
        if race is None:
            abort(404, message="Race {} doesn't exist".format(race_id))

        l = [marshal(r, EventAPI.fields) for r in race.events]
        return l


    def post(self, race_id):
        if request.content_type != 'application/json':
            abort(400, message="Invalid Content-Type")

        data = request.get_json()
        if not isinstance(data, dict):
            data = {}

        race = Race.query.get_or_404(race_id)

        for item in EventListAPI.required_fields:
            if not item in data:
                abort(400, message="Incomplete Request")

        event_number = Event.query.filter(Event.race_id == race_id).count() + 1

        event = Event(race)

        for item in EventListAPI.required_fields:
            event.__setattr__(item, data[item])

        for item in EventListAPI.optional_fields:
            if item in data:
                event.__setattr__(item, data[item])

        event.event_number = event_number

        db.session.add(event)
        db.session.commit()

        return {'message': "Success", 'id': event.id}

class UserSessionListApi(Resource):
    def get(self, user):
        sessions = db.session.query(Session).filter(Session.owner == user).order_by(Session.id)
        return [marshal(s, SessionAPI.fields) for s in sessions]

class UserRaceListApi(Resource):
    def get(self, user):
        races = db.session.query(Race).join(Session).filter(Session.owner == user).order_by(Race.race_number)
        return [marshal(r, RaceAPI.fields) for r in races]


class QueryAPI(Resource):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    def get(self):
        query = request.get_json()

        if query is None:
            return {"message": "Require query data"}, 400, QueryAPI.headers

        if 'query' not in query:
            return {"message": "Require query field in request"}, 400, QueryAPI.headers

        try:
            eq = EventQuery(query['query'], query.get('user', None))
        except:
            return {"message": "Query was invalid"}, 400, QueryAPI.headers
        ret = {
            'query': query['query'],
            'headers': eq.column_names,
            'types': eq.column_types,
            'results': eq.query.all()
        }
        return ret, 200, QueryAPI.headers


    def post(self):
        return self.get()

    def options(self):
        return {}, 200, QueryAPI.headers


class QueryInfoAPI(Resource):
    def options(self):
        return {}, 200, QueryAPI.headers

    def get(self):
        info = LanguageDescription()
        return info.to_dict(), 200, QueryAPI.headers


class SearchAPI(Resource):
    def get(self):
        query = db.session.query(Race)
        for key, value in request.args.iteritems():
            if key == 'player':
                query = query.filter(Race.characters.contains(db.cast([str(value)], ARRAY(db.VARCHAR))))
            elif key == 'course':
                query = query.filter(Race.course == value)

        return [marshal(r, RaceAPI.fields) for r in query]


class TagAPI(Resource):
    def get(self, race_id, user=None):
        query = Event.query.join(Race).join(Session)
        query = query.filter(Event.event_type == "Tag")
        query = query.filter(Event.race_id == race_id)
        query = query.order_by(Event.event_number)
        if user: query = query.filter(Session.owner == user)

        return [marshal(r, EventAPI.fields) for r in query]

class AllTagAPI(TagAPI):
    pass


def configure_resources(api):
    api.add_resource(SessionListAPI, '/sessions')
    api.add_resource(SessionAPI, '/sessions/<int:session_id>')
    api.add_resource(RaceListAPI, '/sessions/<int:session_id>/races')
    api.add_resource(RaceAPI, '/races/<int:race_id>')
    api.add_resource(AllRaceAPI, '/races')
    api.add_resource(EventListAPI, '/races/<int:race_id>/events')
    api.add_resource(EventAPI, '/events/<int:event_id>')
    api.add_resource(UserSessionListApi, '/users/<user>/sessions')
    api.add_resource(UserRaceListApi, '/users/<user>/races')
    api.add_resource(QueryAPI, '/query')
    api.add_resource(QueryInfoAPI, '/query/info')
    api.add_resource(SearchAPI, '/search')
    api.add_resource(AllTagAPI, '/alltags/<int:race_id>')
    api.add_resource(TagAPI, '/tags/<user>/<int:race_id>')

def connect_sqs(app):
    app.sqs_connection = sqs.connect_to_region(app.config['AWS_REGION'])
    app.session_queue = app.sqs_connection.get_queue(app.config['SPLIT_QUEUE'])
    app.session_queue.set_timeout(60*55)
    app.race_queue = app.sqs_connection.get_queue(app.config['PROCESS_QUEUE'])
    app.race_queue.set_timeout(60*55)

