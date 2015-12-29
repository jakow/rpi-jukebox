import flask
class RPJQueue:
    def __init__(self):
        self.queue = []

    def add(self, song):
        self.queue.append(song)

    def get_queue(self):
        q = self.queue  #make a copy?
        return q

    def pop_next(self):
        return self.queue.pop(0)

    def pop(self, i):
        return self.queue.pop(i)

    def remove(self, video_id):
        #if it exists, it will be removed. Otherwise nothing happens
        self.queue = [song for song in self.queue if not (song.get('id') != video_id)]

    def get_json_queue(self):
        return flask.json.jsonify(q=self.queue)

    def flush(self):
      self.queue = []
