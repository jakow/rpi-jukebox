from flask import Flask, render_template, send_from_directory, request, json
import RPJdownloader
import RPJplayer
import RPJqueue
import os
queue = RPJqueue.RPJQueue()
player = RPJplayer.RPJPlayerMplayer(queue)
downloader = RPJdownloader.RPJDownloader()

app = Flask('RPJukebox', static_folder='build/assets', template_folder='build/templates')

# informs the frontend about current queue. Browser will
@app.route('/json_state')
def json_state():
    # jsonify nowPlaying and the song queue to be displayed in the radio
    state = {
         "isPlaying": player.playing,
         "volume": player.volume,
         "nowPlaying": player.now_playing,
         "queue": queue.get_queue()
         }
    return json.jsonify(state)



@app.route('/')
def start_page():
    return render_template('index.html', files=None)

@app.route('/play', methods=['GET'])
def play():
    link = "http://www.youtube.com/watch?v=" + request.args['videoId']
    downloader.background_download(link, onDownloaded=player.play)
    return json_state()
    # return render_template('radio.html', msg="Your download has started. Music will be playing shortly.")


@app.route('/queue_add', methods=['GET'])
def queue_add():
    # to avoid downloading an existing files, implement SQL database
    video_id = request.args['videoId']
    link = "http://www.youtube.com/watch?v=" + video_id
    downloader.background_download(link, callback=queue.add)
    return json_state()


@app.route('/queue_remove', methods=['GET'])
def queue_remove():
    video_id = request.args['videoId']
    queue.remove(video_id)
    return json_state()


@app.route('/pause')
def pause():
    player.pause()
    return json_state()




@app.route('/download_progress')
def download_progress():
    return json.jsonify(downloader.report_progress())

# @app.route('/bower_components/<path:path>')
# def send_bower_components(path):
#    return send_from_directory('bower_components', path)

if __name__  == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')


