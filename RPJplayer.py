from __future__ import unicode_literals

__author__ = 'jakub'
import threading
import os
import pygame
import time
import pyglet
import subprocess
import select
from mplayerWrapper import *


def playback_ended():
  print "Playback ended"


class RPJPlayerPyglet:
  def __init__(self, queue):
    self.queue = queue
    self.player = pyglet.media.Player()
    self.playerThread = threading.Thread()
    self.now_playing = {}
    self.enabled = False
    self.autoplay = True
    self.current_song
    pyglet.options['audio'] = ('openal', 'pulseaudio')

  def play_next(self):
    if self.player.playing:
      self.player.pause()
    print "Playing next"
    song_data = self.queue.pop()
    # self.player = pyglet.media.Player()  # new player needed after previous ends playing...
    song = pyglet.media.load("songs/" + song_data['id'] + ".mp3", streaming=True)
    self.player.queue(song)
    self.player.play()
    if self.autoplay:
      # self.player.on_eos(self.play_next)
      pass

  # function to play desired song, while discarding playlist.
  def play(self, song):
    s = pyglet.media.load("songs/" + song['id'] + ".mp3", streaming=True)
    self.now_playing = song
    # self.player.pitch = 1.5  # LOL
    self.player.queue(s)
    self.player.play()
    if self.autoplay:
      # self.player.on_eos(self.play_next)
      pass

  # function to resume
  def resume(self):
    if not self.player.playing:
      self.player.play()

  def pause(self):
    if self.player.playing:
      self.player.pause()

  @property
  def now_playing(self):
    return self.now_playing

  @property
  def volume(self):
    return self.player.volume

  @volume.setter
  def volume(self, value):
    self.player.volume = value

  @property
  def is_playing(self):
    return self.player.playing


# class RPJPlayerPygame:
#     def __init__(self, queue):
#         self.queue = queue
#         self.player = pygame.mixer.music
#         self.playerThread = threading.Thread()
#         self.nowPlaying = {}
#         self.enabled = False
#         self.autoplay = True
#         pygame.mixer.pre_init(frequency=44100, size=-16, channels=2)
#         pygame.mixer.init()
#
#
#
#     def play(self, song):
#         self.player.load('songs/'+song['id']+'.mp3')
#         self.nowPlaying = song
#         self.player.play()
#
#     def play_next(self):
#         if self.player.get_busy():
#             self.player.pause()
#         print "Playing next"
#         song_data = self.queue.pop()
#         # self.player =  # new player needed after previous ends playing...
#         self.player.load("songs/" + song_data['id'] + ".mp3")
#         self.player.play()
#         if self.autoplay:
#             # self.player.on_eos(self.play_next)
#             pass
#
#     @property
#     def volume(self):
#         return self.player.get_volume()
#
#     @volume.setter
#     def volume(self, value):
#         self.player.set_volume()
#
#     def resume(self):
#         if not self.is_playing:
#             self.player.unpause()
#
#     def pause(self):
#         if self.is_playing:
#             self.player.pause()
#
#     @property
#     def now_playing(self):
#         return self.nowPlaying
#
#     @property
#     def is_playing(self):
#         return self.player.get_busy()


class RPJPlayerMplayer:
    exe_name = 'mplayer' if os.sep == '/' else 'mplayer.exe'

    def __init__(self, queue):
        self.queue = queue
        # self.playerThread = threading.Thread()
        self.nowPlaying = {}
        self.enabled = False
        self.autoplay = True
        self.mplayer = MPlayer()
        self.mplayer.populate()  # populates MPlayer class definitions
        self.volume = 100.0
        self.playing = False

    def __del__(self):
        print 'killing MPlayer'
        # clean up mplayer before quitting
        self.mplayer.quit()

    def play(self, song):
        self.mplayer.stop()
        if isinstance(song, dict):  # if song object is given, assume it is in folder
            self.mplayer.command("loadfile", "songs/" + song['id'] + ".mp3")
        else:  # otherwise just play from path
            print 'loading from file'
            self.mplayer.command("loadfile", song)
        self.nowPlaying = song
        # self.mplayer.volume(self.volume)
        self.playing = True

    def play_next(self):
        print "Playing next"
        song_data = self.queue.pop()
        # self.player =  # new player needed after previous ends playing...
        self.play(song_data)

    @property
    def volume(self):
        return float(self.volume)

    @volume.setter
    def volume(self, value):
        self.volume = value
        if self.is_file_loaded:  # volume can only be set if something is playing
            self.mplayer.volume(value)

    def pause(self):
        if self.is_file_loaded():
            # print 'mplayer reports pause state: ' + str(self.mplayer.command('pausing_keep_force', 'get_property', 'pause'))
            self.mplayer.pause()
            self.playing = not self.playing  # toggle state
        else:
            self.playing = False

    @property
    def now_playing(self):
        return self.nowPlaying

    def is_file_loaded(self):
        output = self.mplayer.get_property('filename')
        # get filename property. If file is loaded, this property contains string starting with A
        print 'get_property(filename): ' + str(output)
        if output:  # check if output is not empty
            if isinstance(output, basestring):  # output can be a base string or a list
                # print 'property is string'
                loaded = (output != 'PROPERTY_UNAVAILABLE')
            else:
                # print 'property is list'
                # check if ANS_filename exists in an array output
                if [s for s in output if "ANS_filename" in s]:
                    loaded = True
                else:
                    loaded = False
            print 'Loaded: ' + str(loaded)
            return loaded
        else:
            return False

    @property
    def playing(self):
        return self.playing

    def seek(self):
        pass

    def position(self):
        pass



if __name__ == '__main__':
    from RPJqueue import RPJQueue
    queue = RPJQueue()
    player = RPJPlayerMplayer(queue)
    time.sleep(5)
    player.is_file_loaded()
    player.is_file_loaded()
    print ''
    print 'Starting playback'
    player.play('/home/jakub/Music/AWESOME.mp3')
    time.sleep(10)
    print 'is playing: ' + str(player.playing) + '\n'
    print 'Now attempting to pause'
    # print 'isloaded: ' + str(player.is_file_loaded())
    player.pause()
    print 'is playing: ' + str(player.playing) + '\n'
    time.sleep(10)
    print 'now resuming'
    player.pause()
    print 'is playing: ' + str(player.playing) + '\n'
    time.sleep(10)
