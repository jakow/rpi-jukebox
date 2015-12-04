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
@app.route('/json_queue')
def json_queue():
    # jsonify nowPlaying and the song queue to be displayed in the radio
    q = {"nowPlaying": player.now_playing(), "is_playing": player.is_playing(), "queue": queue.get_queue()}
    return json.jsonify(q)



@app.route('/')
def start_page():
    return render_template('index.html', files=None, playing=player.is_playing())


@app.route('/radio')
def radio():
    return render_template("radio.html")


@app.route('/play', methods=['GET'])
def play():
    link = "http://www.youtube.com/watch?v=" + request.args['videoId']
    downloader.background_download(link, onDownloaded=player.play)
    return json_queue()
    # return render_template('radio.html', msg="Your download has started. Music will be playing shortly.")


@app.route('/queue_add', methods=['GET'])
def queue_add():
    # to avoid downloading an existing files, implement SQL database, you silly.
    video_id = request.args['videoId']
    link = "http://www.youtube.com/watch?v=" + video_id
    downloader.background_download(link, callback=queue.add(downloader.downloaded))
    return json_queue()


@app.route('/queue_remove', methods=['GET'])
def playlist_remove():
    video_id = request.args['videoId']
    queue.remove(video_id)


@app.route('/html_playlist', methods=['GET'])
def html_playlist():
    pass


@app.route('/pause')
def pause():
    player.pause()
    return json_queue()


@app.route('/resume')
def resume():
    player.resume()
    return json_queue()


@app.route('/download_progress')
def download_progress():
    return json.jsonify(downloader.report_progress())

@app.route('/bower_components/<path:path>')
def send_bower_components(path):
    return send_from_directory('bower_components', path)

if __name__  == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')


