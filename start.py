from flask import Flask, render_template, request
import flask
import RPJdownloader
import RPJplayer
import RPJqueue
from serverSideEvent import *

queue = RPJqueue.RPJQueue()
player = RPJplayer.RPJPlayer(queue)
downloader = RPJdownloader.RPJDownloader()

app = Flask('RPJukebox', static_folder='build/assets', template_folder='build/static-templates')


# set up some event handlers for player
def notify_now_playing_changed():
  sse_publish('nowPlayingChanged', player.now_playing)
def notify_playback_end():
  sse_publish('playbackStopped', get_state())  # queue changes and now playing changes
def notify_queue_changed():
  sse_publish('queueChanged', queue.get_queue())
def notify_downloads_changed():
  sse_publish('downloadsChanged', downloader.report_progress())

player.on('playback_finish', player.load_next)
player.on('playback_finish', notify_playback_end)
player.on('playback_skip', notify_playback_end)
player.on('playback_stop', notify_playback_end)



def get_state():
  return {
    "isPlaying": player.is_playing,
    "volume": player.volume,
    "nowPlaying": player.now_playing,
    "queue": queue.get_queue(),
    "downloads": downloader.report_progress()
  }

@app.route('/')
def start_page():
  return render_template('index.html', files=None)

@app.route('/json_state')
def json_state():
  return flask.json.jsonify(get_state())


@app.route('/subscribe')
def subscribe():
  sse_subscribe()


@app.route('/play', methods=['GET'])
def play():
  link = "http://www.youtube.com/watch?v=" + request.args['videoId']
  downloader.background_download(link, on_downloaded=player.play)
  return json_state()
  # return render_template('radio.html', msg="Your download has started. Music will be playing shortly.")


@app.route('/rewind', methods=['GET'])
def rewind():
  player.seek(0)
  return json_state()


@app.route('/forward', methods=['GET'])
def forward():
  player.play_next()
  return json_state()


@app.route('/queue_add', methods=['GET'])
def queue_add():
  # to avoid downloading an existing files, implement SQL database
  video_id = request.args['videoId']
  link = "http://www.youtube.com/watch?v=" + video_id
  # now decide if we're going to play or enqueue
  if not player.is_playing:
    callback = player.play
  else:
    callback = queue.add
  downloader.background_download(link, on_downloaded=callback)
  return json_state()


@app.route('/queue_remove', methods=['GET'])
def queue_remove():
  index = request.args['index']
  queue.pop(int(index))
  return json_state()


@app.route('/play_pause')
def play_pause():
  player.pause()  # pause/unpause
  # return json.jsonify({"playing": player.is_playing})
  return json_state()


@app.route('/download_progress')
def download_progress():
  return json.jsonify(downloader.report_progress())


if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0')
