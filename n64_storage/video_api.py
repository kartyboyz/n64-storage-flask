

from subprocess import call

from boto import elastictranscoder

from .models import Race, Session
from . import app

import os

def split_video(src, dst, start, end):
    command = ['ffmpeg', '-i', src,
            '-vcodec', 'copy', '-acodec', 'copy',
            '-ss', str(start), '-t', str(end), dst ]
    call(command)

def submit_transcode_job(obj):
    if len(obj.video_url) > 12:
        s3_url = obj.video_url
    else:
        return False
    try:
        full_name = s3_url.split('.com/')[-1]
        name = '/'.join(full_name.split('/')[1:])
        name = name.split('.')[0] + '.mp4'
    except IndexError:
        return False

    print name, full_name

    if isinstance(obj, Race):
        pipeline = app.config['RACE_PIPELINE']
    elif isinstance(obj, Session):
        pipeline = app.config['SESS_PIPELINE']
    else:
        return False

    print pipeline

    prefix = 'encoded/'
    inputs = {
        'Key': full_name,
    }
    outputs = [{
        'Key': name,
        'PresetId': '1351620000001-100070'
    }]
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_KEY')
    et = elastictranscoder.connect_to_region('us-east-1',
            aws_secret_access_key=aws_secret,
            aws_access_key_id=aws_key)

    bucket = 'race-videos' if isinstance(obj, Race) else 'session-videos'
    processed_url = 'https://s3.amazonaws.com/%s/encoded/%s' % (bucket, name)

    if app.config['TRANSCODE']:
        try:
            et.create_job(pipeline, input_name=inputs,
                    outputs=outputs, output_key_prefix=prefix)
            obj.video_processed_url = processed_url
        except:
            return False

    return True
    


