from micropython import const
from config import POWER_SAVE
from time import ticks_ms, ticks_diff, sleep
from widgets import Label
from tempos import sched, do_ntp_sync, key, g
import wifi
from fonts import roboto18,roboto36
import os

class Ring:
    "class used to handle the switch from one app to another in a ring configuration"
    
    INIT  = 0
    END   = 1
    
    def __init__(self, parent):
        self.ring = []
        self.names = []
        self.curr = 0
        parentname = getattr(parent, "__name__")
        appslist = os.listdir(parentname)
        for f in appslist:
            mm = f.split(".")[0]
            try:
                __import__(parentname + "." + mm)
                self.names.append(mm)
                self.ring.append(getattr(parent, mm))
            except Exception as e:
                print("{} : {} : {}".format(mm, type(e).__name__, e))

    def mod(self, a):
        n = len(self.ring)
        return a - n if a >= n else a + n if a < 0 else a

    def call(self, i, fn):
        if i < 0 or i >= len(self.ring):
            return
        try:
            if fn == 0:
                self.ring[i].app_init()
            elif fn == 1:
                self.ring[i].app_end()
        except Exception as e:
            print("{} : {} : {}".format(self.names[i], type(e).__name__, e))

    def begin(self):
        if len(self.ring) == 0:
            return
        self.call(self.curr, self.INIT)
        

    def end(self):
        if len(self.ring) == 0:
            return
        self.call(self.curr, self.END)
        

    def switch(self, inc):
        nxt = self.mod(self.curr + inc)
        if nxt == self.curr:
            return
        self.end()
        self.curr = nxt
        self.begin()

    def find(self, name):
        try:
            return self.names.index(name)
        except:
            return -1

_APP_LOCK = False


def setapplock(b):
    global _APP_LOCK
    _APP_LOCK = b

import apps

appRing = Ring(apps)

def _move(inc):
    global  appRing, _APP_LOCK
    if _APP_LOCK:
        return
    appRing.switch(1)
        

key.addListener(_move)


sleep(1)
g.setfont(roboto36)
g.fill_rect(100,100,200,40,0)
g.text('Setting Clock', 100, 100)
g.show()

status = Label(g,20, 260, 160, 40, roboto18, 1)
progress = Label(g,200, 260, 40, 40, roboto18, 1)
wifi.setScheduler(sched)
wifi.do_connected_action(do_ntp_sync,status,progress)   
appRing.begin()
sched.set_lightsleep(POWER_SAVE)
sched.run()
 