from __future__ import unicode_literals
import mplayer, time
import json
from mplayer import CmdPrefix
import eventlet

__author__ = 'Jakub'

eventlet.monkey_patch(all=True)

class RPJPlayer(object):
    """ RPJ wrapper for Mplayer Python wrapper
     Communicates with Mplayer via sockets and so is completely asynchronous """

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
        self.queue = queue  # use queue object to fetch next
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
        if isinstance(song, dict):  # check if a song dict is given
            path = 'songs/' + song['id'] + '.mp3'
        else:  # otherwise load from path
            path = song
        self.player.loadfile(path)
        if self._paused:
            self.pause()  # unpause
        self.nowPlaying = song

    def play_next(self):
        if not self.queue.empty:  #
            self.play(self.queue.pop(0))
        else:
            raise Exception('Popping from empty queue')

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

    @property
    def loaded_file(self):
        return self.player.filename

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

    def detach_handlers(self, event='all'):
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
        else:
            print 'mplayer pipe: ' + data


def notifying(func):
    def notifying_function(*args, **kwargs):
        return_val = func(*args, **kwargs)
        args[0].execute_event_hooks()
        return return_val

    return notifying_function


class RPJPlayerV2(object):
    def __init__(self, workingDirectory='songs'):
        # set up working directory:
        # assert isinstance(workingDirectory, str)
        self.workingDirectory = workingDirectory if workingDirectory.endswith('/') else workingDirectory + '/'
        # set up mplayer
        self._mplayer = mplayer.Player(autospawn=False)
        self._mplayer.args = ['-really-quiet', '-msglevel', 'global=6']

        # set up event handlers (private) and hooks (public)
        self._event_handlers = {"playback_finish": [],
                                "playback_skip": [],
                                "playback_stop": []
                                }
        self._event_hooks = []
        self._mplayer.stdout.connect(self._playback_end_event_handler)

        # now set up state
        self._queue = []
        self._now_playing = {}
        self._is_playing = False
        self._paused = False
        self._vol = 100
        self._randomize = False
        self._loop = False
        # then spawn mplayer
        self._mplayer.spawn()
        self._mplayer.volume = self._vol

    def state(self):
        return json.dumps({
            "is_playing": self._is_playing, # will change
            "now_playing": self._now_playing,
            "position": self._mplayer.time_pos,
            "volume": self._vol,
            "randomize": self._randomize,
            "loop": self._loop,
            "queue": self._queue
        })

    # load file for playback and play immediately
    @notifying
    def load(self, song):
        if isinstance(song, dict):  # check if a song dict is given
            path = self.workingDirectory + song['id'] + '.mp3'
        else:  # otherwise load from path
            path = self.workingDirectory + song
        self._now_playing = song
        self._mplayer.loadfile(path)
        self._is_playing = True
        if self._paused:  # unpause
            self.pause()

    @notifying
    def play_pause(self):
        self._paused = not self._paused
        self._mplayer.pause()

    @notifying
    def addToQueue(self, song, index=None):
        if index is None:
            self._queue.append(song)
        else:
            self._queue.insert(song, index)

    # ---------------- PROPERTIES ----------------

    @property
    def volume(self):
        return self._vol

    @volume.setter
    def volume(self, value):
        self._mplayer.volume = value
        self._vol = value

    @property
    def time_pos(self):
        return self._mplayer.time_pos

    @time_pos.setter
    def time_pos(self, value):
        self._mplayer.time_pos = value

    @property
    def percent_pos(self):
        return self._mplayer.percent_pos

    @time_pos.setter
    def time_pos(self, value):
        self._mplayer.percent_pos = value


    # ------------ EVENTS, HOOKS, etc ----------------
    def on(self, event_name, handler):
        if event_name in self._event_handlers:
            self._event_handlers[event_name].append(handler)

    def detach_handlers(self, event='all'):
        if event == 'all':
            self._event_handlers["playback_finish"] = []
            self._event_handlers["playback_skip"] = []
            self._event_handlers["playback_stop"] = []
        elif event in self._event_handlers:
            self._event_handlers[event] = []

    def execute_event_hooks(self):
        #executes all the function hooks asynchronously as greenlets
        def pr():
            print self.state()
        eventlet.spawn(pr)
        for hook in self._event_hooks:
            eventlet.spawn(hook)

    def _playback_end_event_handler(self, data):
        if data.startswith('EOF code: '):
            # print data
            self._is_playing = False
            code = int(data[len('EOF code: '):])
            if code == 1:
                # print 'RPJPlayer: playback finished'
                handlers = self._event_handlers['playback_finish']
            elif code == 2:
                # print 'RPJPlayer: playback skipped'
                handlers = self._event_handlers['playback_skip']
            elif code == 4:
                # print 'RPJPlayer: playback stopped'
                handlers = self._event_handlers['playback_stop']
            else:
                handlers = None

            if handlers:
                for handler in handlers:
                    handler()
            self.execute_event_hooks()
            # print 'mplayer pipe: ' + data




if __name__ == '__main__':
    # some test routines
    import RPJqueue

    p = RPJPlayerV2(workingDirectory='songs')
    time.sleep(3)
    p.load('w9QfN-ODGWM.mp3')
    time.sleep(10)
    p.addToQueue('w9QfN-ODGWM.mp3')
    p.addToQueue('SYM-RJwSGQ8.mp3')
    print p.volume
    p.load('SYM-RJwSGQ8.mp3')
    time.sleep(10)
    print p.percent_pos
    time.sleep(2)
    # p.on('playback_finish', printeof)
    # p.play('w9QfN-ODGWM')
    # print p.percent_pos

    # p.quit()
