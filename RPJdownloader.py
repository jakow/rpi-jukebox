from __future__ import unicode_literals
__author__ = 'jakub'
import threading
import youtube_dl
import os
import RPJplayer


class RPJDownloader:


    def __init__(self):
        self.options = {
            'format': 'bestaudio/best', # choice of quality
            'extractaudio' : True,      # only keep the audio
            'audioformat' : 'mp3',      # convert to ogg
            'outtmpl': 'songs/%(id)s'+'.mp3',     # name the file the id of the video
            'noplaylist' : True,        # only download single song, not playlist
            }
        self.ydl = youtube_dl.YoutubeDL(self.options)
        self.downloadList = []
        self.backgroundThread = threading.Thread()
        self.downloaded = []
        self.progressLock =threading.Lock()
        self.ydl.add_progress_hook(self.update_progress)
        self.progress = {}
        self.now_downloading = {}

    def report_progress(self):
        with self.progressLock:
          progress = {
            "nowDonwloading": self.now_downloading,
            "progress": self.progress,
            "remaining": self.downloadList
          }

    def background_download(self, video, **kwargs):
        with self.progressLock:
            self.downloadList.append(video)
        if not self.backgroundThread.is_alive():
            self.backgroundThread = threading.Thread(target=self.background_download_daemon, kwargs=kwargs)
            self.backgroundThread.start()

    def background_download_daemon(self, **kwargs):
        print 'Background download launched'
        self.downloaded = []
        while self.downloadList:
            video = self.downloadList.pop(0)
            with self.progressLock:  # update the currently downloaded file
                self.now_downloading = video
            result = self.ydl.extract_info(video, download=True)
            if 'entries' in result:
                # Can be a playlist or a list of videos
                file_info  = result['entries'][0]
            else:
                file_info = result
            print "Downloading " + file_info['title']
            with self.progressLock:
                self.now_downloading = file_info
            self.downloaded.append(file_info)

        # f exists, call a callback function, which will execute after the download has completed
        if 'onDownloaded' in kwargs:  # check if we are doing anything
            callback = kwargs['onDownloaded']
            if 'param' in kwargs:
                param = kwargs['param']
                print 'on download ' + callback.__name__ + '(' + param.__name__ + ')'
                return callback(param)
            else:
                print 'on download ' + callback.__name__ + '(last_downloaded_file)'
                return callback(file_info)
        else:
            return None

    def last_downloaded(self):
        return self.downloaded

    def is_downloading(self):
        return self.backgroundThread.is_alive()

    def update_progress(self, status):
        with self.progressLock: #lock to prevent concurrent access
            self.progress = status  # copy the progress kwars

    def now_downloading(self):
        with self.progressLock: # copy with lock
            p = self.progress
        return p



