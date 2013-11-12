
from flask import Flask
from flask import request
from flask.ext.restful import Api, Resource, marshal, fields, abort

from .models import Session, Race, db

from subprocess import call
import hashlib, tempfile, urllib2, os

def split_video(src, dst, start, end):
    command = ['ffmpeg', '-i', src, 
            '-vcodec', 'copy', '-acodec', 'copy',
            '-ss', str(start), '-t', str(end), dst ]
    call(command)

class VideoSplitAPI(Resource):

    server_folder = '/home/michael/vid_test/races/{}/'
    server = 'http://192.168.98.180:8888/races/{}/{}.{}'

    def post(self, session_id):
        session = Session.query.get_or_404(session_id)

        vid = self.download_race(session)
        ext = session.video_url.split('.')[-1]
        
        for race in session.races:
            newfile = self.split_race(vid, race, ext)
            race.video_url = VideoSplitAPI.server.format(session_id, race.id, ext)
            race.video_split = True
            db.session.add(race)
        session.video_split = True
        db.session.add(session)
        db.session.commit()

        return {'message':'Video Split Successful'}


    def download_race(self, session):

        f = tempfile.NamedTemporaryFile()
        chunk_size = 4 * 1024 * 1024
        try:
            req = urllib2.urlopen(session.video_url)
            while True:
                chunk = req.read(chunk_size)
                if not chunk: break
                f.write(chunk)
            f.flush()
            return f

        except urllib2.HTTPError:
            print "Couldn't download ", session
            return None
        except urllib2.URLError:
            print "Couldn't download ", session
            return None
        

    def split_race(self, video, race, ext):
        try:
            os.mkdir(VideoSplitAPI.server_folder.format(race.session_id))
        except OSError as e:
            if e.errno != 17:
                raise e

        dest = VideoSplitAPI.server_folder.format(race.session_id) + '/{}.{}'
        dest = dest.format(race.id, ext)
        split_video(video.name, dest, race.start_time, race.duration)
        return dest

def configure_resources(api):
    api.add_resource(VideoSplitAPI, '/sessions/<int:session_id>/split_races')

