import flask


class RPJQueue:
    def __init__(self):
        self.queue = []

    def add(self, song):
        self.queue.append(song)

    def get_queue(self):
        q = self.queue  # make a copy?
        return q

    def pop(self):
        return self.queue.pop(0)

    def pop(self, i):
        return self.queue.pop(i)

    def remove(self):
        print 'Removed ', self.queue.pop(0).title, ' from queue'

    def removeById(self, video_id):

        #if it exists, it will be removed. Otherwise nothing happens
        if isinstance(video_id, basestring):
            self.queue = [song for song in self.queue if not (song.get('id') == video_id)]


    @property
    def empty(self):
        print 'queue empty? ', not self.queue
        return not self.queue

    def jsonify(self):
        return flask.json.jsonify(q=self.queue)

    def flush(self):
      self.queue = []
