from __future__ import unicode_literals

__author__ = 'jakub'
import threading
import youtube_dl
import os
import RPJplayer
import gevent


class RPJDownloader:
    def __init__(self):
        self.options = {
            'format': 'bestaudio/best',  # choice of quality
            'extractaudio': True,  # only keep the audio
            'audioformat': 'mp3',  # convert to ogg
            'outtmpl': 'songs/%(id)s' + '.mp3',  # name the file the id of the video
            'noplaylist': True,  # only download single song, not playlist
        }
        self.ydl = youtube_dl.YoutubeDL(self.options)
        self.downloadQueue = []
        self.backgroundThread = threading.Thread()
        self.downloaded = []
        self.progressLock = threading.Lock()
        self.ydl.add_progress_hook(self.update_progress)
        self.now_downloading = {}

    def report_progress(self):
        with self.progressLock:
            return {
                "now_downloading": self.now_downloading,
                "remaining_downloads": self.downloadQueue
            }

    def background_download(self, video, **kwargs):
        with self.progressLock:
            self.downloadQueue.append(video)
        if not self.backgroundThread.is_alive():
            self.backgroundThread = threading.Thread(target=self.background_download_daemon, kwargs=kwargs)
            self.backgroundThread.start()

    def background_download_daemon(self, **kwargs):
        print 'Background download launched'
        self.downloaded = []
        while self.downloadQueue:
            video = self.downloadQueue.pop(0)
            with self.progressLock:  # update the currently downloaded file
                self.now_downloading = video
            result = self.ydl.extract_info(video, download=False)
            if 'entries' in result:
                # Can be a playlist or a list of videos
                file_info = result['entries'][0]
            else:
                file_info = result
            print "Downloading " + file_info['title']
            with self.progressLock:
                self.now_downloading = file_info
            self.ydl.download([video])
            self.downloaded.append(file_info)
    # f exists, call a callback function, which will execute after the download has completed
            if 'on_downloaded' in kwargs:  # check if we are doing anything
                callback = kwargs['on_downloaded']
                if 'param' in kwargs:
                    param = kwargs['param']
                    print 'on download ' + callback.__name__ + '(' + param.__name__ + ')'
                    callback(file_info, param)
                else:
                    print 'on download calling ' + callback.__name__ + ' with last downloaded file object'
                    callback(file_info)


    def last_downloaded(self):
        return self.downloaded


    def is_downloading(self):
        return self.backgroundThread.is_alive()


    def update_progress(self, status):
        with self.progressLock:  # lock to prevent concurrent access
            self.now_downloading = status  # copy the progress kwars
