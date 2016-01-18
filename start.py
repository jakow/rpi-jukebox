from flask import Flask, render_template, request
from gevent.wsgi import WSGIServer
import flask
import RPJdownloader
import RPJplayer
import RPJqueue
import signal
from serverSideEvent import *
from gevent import monkey

queue = RPJqueue.RPJQueue()
player = RPJplayer.RPJPlayer(queue)
downloader = RPJdownloader.RPJDownloader()

app = Flask('RPJukebox', static_folder='build/assets', template_folder='build/static-templates')


def get_state():
    return {
        "isPlaying": player.is_playing,
        "volume": player.volume,
        "position": player.time_pos,
        "nowPlaying": player.now_playing,
    }


def notify_state_changed():
    print 'publishing state change'
    sse_publish('stateChanged', get_state())  # queue changes and now playing changes


def notify_queue_changed():
    print 'publishing queue change'
    sse_publish('queueChanged', queue.get_queue())


def notify_downloads_changed():
    sse_publish('downloadsChanged', downloader.report_progress())

def reload_last():
    if queue.empty:
        player.play(player.nowPlaying) # play last played song
        player.pause() # and pause immediately
# set up some event handlers for player
player.on('playback_finish', reload_last)
player.on('playback_finish', notify_state_changed)
player.on('playback_skip', notify_state_changed)
player.on('playback_stop', notify_state_changed)


@app.route('/')
def start_page():
    return render_template('index.html', files=None)


@app.route('/json_state')
def json_state():
    return flask.json.jsonify(get_state())


@app.route('/json_queue')
def json_queue():
    return flask.json.jsonify({"queue": queue.get_queue()})


@app.route('/subscribe')
def subscribe():
    return sse_subscribe()


@app.route('/play', methods=['GET'])
def play():
    link = "http://www.youtube.com/watch?v=" + request.args['videoId']

    def callback(song):
        player.play(song)
        notify_state_changed()

    downloader.background_download(link, on_downloaded=callback)

    return json_state()
    # return render_template('radio.html', msg="Your download has started. Music will be playing shortly.")


@app.route('/rewind', methods=['GET'])
def rewind():
    player.seek(0)
    notify_state_changed()
    return json_state()


@app.route('/forward', methods=['GET'])
def forward():
    player.play_next()
    notify_state_changed()
    notify_queue_changed()
    return json_state()


@app.route('/queue_add', methods=['GET'])
def queue_add():
    # to avoid downloading an existing files, implement SQL database
    video_id = request.args['videoId']
    link = "http://www.youtube.com/watch?v=" + video_id

    # now decide if we're going to play or enqueue
    def callback(song):
        if player.is_playing:
            queue.add(song)
            notify_queue_changed()
        else:
            player.play(song)
            notify_state_changed()

    downloader.background_download(link, on_downloaded=callback)
    # notify_queue_changed()

    return json_state()


@app.route('/queue_remove', methods=['GET'])
def queue_remove():
    index = request.args['index']
    if index is not None:
        queue.pop(int(index))
        notify_queue_changed()
    return json_state()


# use this to toggle paused state
@app.route('/pause')
def toggle_pause():
    player.pause()  # pause/unpause
    # return json.jsonify({"playing": player.is_playing})
    notify_state_changed()
    return json_state()


@app.route('/download_progress')
def download_progress():
    notify_downloads_changed()
    return flask.json.jsonify(downloader.report_progress())


if __name__ == '__main__':
    gevent.signal(signal.SIGQUIT, gevent.kill)
    app.debug = True
    server = WSGIServer(("", 5000), app)
    server.serve_forever()
