import json
import os
import uuid
import tempfile

from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.internet import reactor, threads

import process_audio
import urllib
import requests

# Process over HTTP

POST_URL = 'https://voxanon.knowtheory.net/messages/notify'
PROCESS_ROOT = 'https://process.text.audio/'

filter_opts = ['raw', 'half', 'double', 'blend', 'flat', 'blur3', 'blur30', 'fast', 'slow']


class Process(Resource):
    def __init__(self, rootdir):
        self.rootdir = rootdir
        Resource.__init__(self)

    def next_id(self):
        uid = None
        while uid is None or os.path.exists(os.path.join(self.rootdir, uid)):
            uid = uuid.uuid4().get_hex()[:16]
        return uid

    def render_POST(self, req):
        cmd = json.load(req.content)

        audio_url = cmd['fb_audio_url']

        reactor.callInThread(self.do_process, cmd)

        return 'thanks!'

    def do_process(self, cmd):
        uid = self.next_id()
        
        # Download audio
        a_url = cmd['fb_audio_url']
        with tempfile.NamedTemporaryFile(suffix=a_url.split('.')[-1]) as fp:

            print 'downloading', a_url
            urllib.urlretrieve(a_url, filename=fp.name)

            print 'processing'
            process_audio.process(fp.name, os.path.join(self.rootdir, uid))

        cmd['process_uid'] = uid
        cmd['filters'] = {}
        for name in filter_opts:
            cmd['filters'][name] = PROCESS_ROOT + uid + '/%s.mp3' % (name)

        # Done! Notify
        print 'done!', uid, 'posting', cmd
        requests.post(POST_URL, json=cmd)
        print 'ok'

if __name__=='__main__':
    MEDIA_ROOT = 'media'
    port = 7890
    interface = '0.0.0.0'

    try:
        os.makedirs(MEDIA_ROOT)
    except OSError:
        pass

    f = File(MEDIA_ROOT)

    f.putChild('process', Process(MEDIA_ROOT))

    s = Site(f)
    reactor.listenTCP(port, s, interface=interface)
    print 'http://%s:%d' % (interface, port)
    reactor.run()
    
