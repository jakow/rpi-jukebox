from __future__ import unicode_literals
from mplayerWrapper import *
import mplayer, asyncore, time, threading
from mplayer import CmdPrefix
__author__ = 'Jakub'

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
        self.playback_finish_handlers = []
        self.playback_skip_handlers = []
        self.playback_stop_handlers = []
        self._event_handlers = {"playback_finish": [],
                                "playback_skip": [],
                                "playback_stop": []
                                }

        self.player.stdout.connect(self._playback_end_event)

        # now set up state variables
        self.queue = queue # use queue object to fetch next
        self.nowPlaying = {}
        self._paused = False
        self.vol = 100
        # then spawn mplayer
        self.player.spawn()
        self.player.volume = self.vol

    def __del__(self):
        print 'quitting mplayer'
        self.player.quit()

    # Play function. Will emit on_eof event when playback is finished
    def play(self, song):
        if isinstance(song, dict): # check if a song dict is given
            path = 'songs/' + song['id'] + '.mp3'
        else: # otherwise load from path
            path = song
        self.player.loadfile(path)
        if self._paused:
            self.pause()  # unpause
        self.nowPlaying = song

    def play_next(self):
        if not self.queue.empty: #
            self.play(self.queue.pop(0))
        else:
            self.play(self.nowPlaying) # reload last file
            self.pause() # pause immediately

    def pause(self):
        if self.player.filename is not None:  # pausing when there is no file loaded is meagningless
            self.player.pause()  # pause/unpause
            self._paused = not self._paused  # toggle state

    def stop(self):
        self.player.stop()

    @property
    def percent_pos(self):
        return self.player.percent_pos

    @percent_pos.setter
    def percent_pos(self, value):
        self.player.percent_pos = value

    @property
    def time_pos(self):
        return self.player.time_pos

    @time_pos.setter
    def time_pos(self, value):
        self.player.percent_pos = value

    @property
    def volume(self):
        return self.vol

    @volume.setter
    def volume(self, value):
        self.player.volume = value
        self.vol = value

    @property
    def now_playing(self):
        return self.nowPlaying


    def seek(self, value, type='absolute'):
        if type == 'percent':
            self.player.percent_pos = value
        elif type == 'absolute':
            self.player.time_pos = value


    @property
    def is_playing(self):
        # playing: if not paused and there is a file loaded
        return (not self._paused) and (self.player.filename is not None)

    def on(self, event_name, handler):
        if event_name in self._event_handlers:
            self._event_handlers[event_name].append(handler)


    def detach_handlers(self, event = 'all'):
        if event == 'all':
            self._event_handlers["playback_finish"] = []
            self._event_handlers["playback_skip"] = []
            self._event_handlers["playback_stop"] = []
        elif event in self._event_handlers:
            self._event_handlers[event] = []


    def quit(self):
        self.player.quit()

####### PRIVATE METHODS ##########################3333

    def _playback_end_event(self, data):
        if data.startswith('EOF code: '):
            print data
            self.playing = False
            code = int(data[len('EOF code: '):])
            if code == 1:
                print 'RPJPlayer: playback finished'
                handlers = self._event_handlers['playback_finish']
            elif code == 2:
                print 'RPJPlayer: playback skipped'
                handlers = self._event_handlers['playback_skip']
            elif code == 4:
                print 'RPJPlayer: playback stopped'
                handlers = self._event_handlers['playback_stop']
            else:
                handlers = None

            if handlers:
                for handler in handlers:
                    handler()


if __name__ == '__main__':
  # some test routines
    import RPJqueue
    queue = RPJqueue.RPJQueue()
    p = RPJPlayer(queue)

    def printeof():
        print 'EOF!'

    p.on('playback_finish', printeof)
    p.play('w9QfN-ODGWM')
    print p.percent_pos
    time.sleep(3)
    p.quit()
