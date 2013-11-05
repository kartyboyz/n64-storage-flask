
import os
import unittest
import json

from . import app, api, models
from .models import Session, Race

import pdb


class StorageTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client()
        models.db.create_all()
        s = [Session(), Session(), Session()]
        r = [Race(s[0], '', 1), Race(s[0], '', 2)]
        for i in s: models.db.session.add(i)
        for i in r: models.db.session.add(i)
        models.db.session.commit()


    def tearDown(self):
        models.db.drop_all()


    def test_models(self):
        s = Session('url')
        r1 = Race(s, 'url2', 4)
        r2 = Race(s, 'url3', 5)
        models.db.session.add(s)
        models.db.session.add(r1)
        models.db.session.add(r2)
        models.db.session.commit()

        assert s.id is not None
        assert r1.session_id == s.id
        assert r2.session_id == s.id
        assert r1.id != r2.id


    def test_session_list_get(self):
        resp = self.app.get('/sessions')
        assert resp.status_code == 200
        assert resp.content_type == 'application/json'
        data = json.loads(resp.data)
        assert isinstance(data, list)


    def test_session_list_post(self):                           
        resp = self.app.post('/sessions', data=json.dumps(str(dict())))
        assert resp.status_code != 200                           
        resp = self.app.post('/sessions', data=json.dumps(str(dict())),
                content_type='application/json')                  
        assert resp.status_code == 200                             
        data = json.loads(resp.data)                                
        assert 'id' in data                                          


    def test_sesion_get(self):
        resp = self.app.get('/sessions/2312341231252')
        assert resp.status_code == 404
        resp = self.app.get('/sessions/1')
        assert resp.status_code == 200
        
        data = json.loads(resp.data)
        assert 'video_url' in data
        assert 'id' in data
        assert data['id'] == 1
        assert 'date' in data
        assert 'video_split' in data


    def test_session_put(self):
        self.app.put('/sessions/1', data=json.dumps({'video_url':'my_url'}),
                content_type='application/json')
        resp = self.app.get('/sessions/1')
        assert 'my_url' in resp.data


    def test_session_delete(self):
        resp = self.app.get('/sessions/2')
        assert resp.status_code == 200
        self.app.delete('/sessions/2')
        resp = self.app.get('/sessions/2')
        assert resp.status_code == 404


    def test_race_list_get(self):
        resp = self.app.get('/sessions/1/races')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert len(data) > 0
        resp = self.app.get('/sessions/13412341234/races')
        assert resp.status_code == 404

    
    def test_race_list_post(self):
        pass


    def test_race_get(self):
        pass

    def test_race_put(self):
        pass

    def test_race_delete(self):
        pass
