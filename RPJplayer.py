from __future__ import unicode_literals
from mplayerWrapper import *
import mplayer, asyncore, time, threading
from mplayer.async import AsyncPlayer
__author__ = 'Jakub'

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
        self.eof_handler = {}

    def __del__(self):
        print 'killing MPlayer'
        # clean up mplayer before quitting
        self.mplayer.quit()

    def play(self, song):
        self.mplayer.stop()
        if isinstance(song, dict):  # if song object is given, assume it is in folder
            self.mplayer.command("loadfile", "songs/" + song['id'] + ".mp3")
            self.nowPlaying = song
        else:  # otherwise just play from path
            print 'loading from file'
            self.mplayer.command("loadfile", song)
        self.mplayer.volume(self.volume)
        self.playing = True
        while not self.is_eof():
            time.sleep(1)
        self.eof_event()

    # EOF events
    def on_eof(self, handler, *args):
        if args:
            self.eof_handler = {'handler': handler, 'args': args}
        else:
            self.eof_handler = {'handler': handler}

    def eof_event(self):
        print 'end of playback'
        if 'args' in self.eof_handler:  # if args are empty
            self.eof_handler['handler'](self.eof_handler['args'])
        else:
            self.eof_handler['handler']()

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
        output = self.mplayer.command('pausing_keep_force', 'get_property', 'filename')
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

    def seek(self, value, type):
        if type == 'percentage':
            self.mplayer.command('pausing_keep_force', 'seek', 1)
        elif type == 'absolute':
            self.mplayer.command('pausing_keep_force', 'seek', 2)

    def is_eof(self):
        self.mplayer.flush_pipe()
        pipe = self.mplayer.command('pausing_keep_force', 'get_property', 'percent_pos')[0]
        return pipe.find('percent') < 0

    def get_position(self):
        self._parse_property('po')

    def _parse_property(self, property):
        raw = self.mplayer.command('pausing_keep_force', 'get_property', property)
        print 'get_property(filename): ' + str(raw)
        prop = "ANS_"+ property
        if raw:  # check if raw output is not empty
            if isinstance(raw, basestring):  # output can be a base string or a list
                if raw.find(prop) >= 0:
                    return raw[len(prop):]
                else:
                  print 'error reading property'
                  return "PROPERTY_UNAVAILABLE"
            else:  # if not string then list
                # check if ANS_filename exists in an array output
                find_prop = next((s for s in raw if prop in raw), "PROPERTY_UNAVAILABLE")
                return find_prop


class RPJPlayer(object):
    """ RPJ wrapper for Mplayer Python wrapper """
    def __init__(self, queue):
        # set up mplayer
        self.player = mplayer.Player(autospawn=False)
        self.player.args = ['-really-quiet', '-msglevel', 'global=6']

        # set up event handlers
        self.playback_finish_handler = None
        self.playback_skip_handler = None
        self.playback_stop_handler = None
        self.player.stdout.connect(self._playback_end_event)

        # now set up state variables
        self.queue = queue # use queue object to fetch next
        self.nowPlaying = {}
        self.playing = False

        # then spawn mplayer
        self.player.spawn()

    def __del__(self):
        print 'quitting mplayer'
        self.player.quit()

    # Play function. Will emit on_eof event when playback is finished
    def play(self, song):
        if isinstance(song, dict): # check if a song dict is given
            path = 'songs/' + song['id'] + '.mp3'
        else:
            path = 'songs/' + song + '.mp3'

        self.player.loadfile(path)
        if self.player.filename is not None:
            self.playing = True
            self.nowPlaying = song

    def play_next(self):
        if not self.queue.empty:
            self.play(self.queue.pop())

    def pause(self):
        if self.player.filename is not None:
            self.player.pause()  # pause/unpause
            self.playing = not self.playing  # toggle state

    def stop(self):
        self.player.stop()

    @property
    def percent_pos(self):
        return self.player.percent_pos

    @percent_pos.setter
    def percent_pos(self, value):
        self.player.percent_pos = value

    @property
    def volume(self):
        return self.player.volume

    @volume.setter
    def volume(self, value):
        self.player.volume = value

    def on_playback_finish(self, handler):
        self.playback_finish_handler = handler

    def on_playback_skip(self, handler):
        self.playback_skip_handler = handler

    def on_playback_stop(self, handler):
        self.playback_stop_handler = handler

    def quit(self):

        self.player.quit()

####### PRIVATE FUNCTIONS ##########################3333

    def _playback_end_event(self, data):
        if data.startswith('EOF code: '):
            print data
            self.playing = False
            code = int(data[len('EOF code: '):])
            if code == 1:
                print 'RPJPlayer: playback finished'
                handler = self.playback_finish_handler
            elif code == 2:
                print 'RPJPlayer: playback skipped'
                handler = self.playback_skip_handler
            elif code == 4:
                print 'RPJPlayer: playback stopped'
                handler = self.playback_stop_handler
            else:
                handler = None

            if handler is not None:
                handler()


# if __name__ == '__main__':
#     def done():
#         print 'Done playing!'
#     from RPJqueue import RPJQueue
#     queue = RPJQueue()
#     player = RPJPlayerMplayer(queue)
#     player.is_file_loaded()
#     player.is_file_loaded()
#     print ''
#     print 'Starting playback'
#     player.on_eof(done)
#     player.play('/home/jakub/Programming/rpi-jukebox/songs/w9QfN-ODGWM.mp3')
#
    #
    # time.sleep(10)
    # print 'is playing: ' + str(player.playing) + '\n'
    # print 'Now attempting to pause'
    # # print 'isloaded: ' + str(player.is_file_loaded())
    # player.pause()
    # print 'is playing: ' + str(player.playing) + '\n'
    # time.sleep(5)
    # print 'now resuming'
    # player.pause()
    # print 'is playing: ' + str(player.playing) + '\n'
    # time.sleep(5)
    # print 'seeking'
    # player.foo()
    # time.sleep(3)
    # print 'is EOF? ' + str(player.is_EOF())
    # print 'looping'
    # for x in xrange(20):
    #     print 'playing: ' + str(player.bar())
    #     time.sleep(1)
    # print "EOF: " + str(player.is_EOF())
    #
    #
    #




if __name__ == '__main__':
    import RPJqueue
    queue = RPJqueue.RPJQueue()
    p = RPJPlayer(queue)

    def printeof():
        print 'EOF!'


    p.on_playback_finish(printeof)
    p.play('w9QfN-ODGWM')
    print p.percent_pos
    time.sleep(3)
    p.quit()
