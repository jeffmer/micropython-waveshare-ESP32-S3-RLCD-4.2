import ure
import time
import requests
import math
import wifi
from fonts import roboto18, roboto24, roboto36
from wifi import connect, lazy_disconnect
from widgets import Label, BatteryMeter, smallClock
import ntptime
from tempos import g, sched, getBatPercent
from micropython import const
from config import summertime

BLACK = const(0)
WHITE = const(1)

_time_offset = 3600 if summertime else 0
_bus_stop = "490009652"
_bus_stop_name = "Mariner Gardens"

def parseDateTime(datestr):
    regex = "^(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)Z$"
    match = ure.match(regex, datestr)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        seconds = int(match.group(6))
        return time.mktime((year, month, day, hour, minute, seconds,0,0))
    else:
        return None
       
def getdelay(ts):
    global _time_offset
    at = parseDateTime(ts)
    if at is None:
        return None
    secs = at + _time_offset - time.time()
    return int(secs/60)


def bustimes(naptanId,direction):
    URL = "https://api.tfl.gov.uk/StopPoint/{}/Arrivals".format(naptanId+direction)
    r = requests.get(URL)       
    dd = r.json()
    res = []
    for el in dd:
        line = el["lineName"]
        dest = el["destinationName"]
        dest = (dest.split(","))[0]
        arrival = el["expectedArrival"]
        r = (line,dest,getdelay(arrival))
        res.append(r)
    res.sort(key=lambda e : e[2])
    return res
  
XOFFSET = const(80)
YOFFSET = const(30)

def draw_title(now):
    global _bus_stop, _bus_stop_name
    g.fill(BLACK)
    g.setfont(roboto24)
    g.fill_rect(XOFFSET,YOFFSET,240,40, WHITE)
    g.setfontalign(0, 0)
    g.text(_bus_stop_name, XOFFSET+120, YOFFSET+20, BLACK)
    if now:
        g.show()
        
def draw_all():
    global _bus_stop, XOFFSET    
    draw_title(False)
    north = bustimes(_bus_stop,"N")
    south = bustimes(_bus_stop,"S")
    north.extend(south)
    north.sort(key=lambda e : e[2])
    y = YOFFSET+50
    g.setfont(roboto18)
    g.setfontalign(-1, -1)
    g.text("Bus",XOFFSET+10,y,WHITE)
    g.setfontalign(0, -1)
    g.text("Destination",XOFFSET+120,y,WHITE)
    g.setfontalign(1, -1)
    g.text("Min",XOFFSET+230,y,WHITE)
    y +=30
    g.line(XOFFSET+10,y,XOFFSET+230,y,WHITE)
    y+=10
    g.setfont(roboto24)
    for b in north:
        g.setfontalign(-1, -1)
        g.text(b[0],XOFFSET+10,y,WHITE)
        g.setfontalign(0, -1)
        g.text(b[1],XOFFSET+120,y,WHITE)
        g.setfontalign(1, -1)
        g.text("due" if b[2]==0 else str(b[2]),XOFFSET+230,y,WHITE)
        y+=35
        if y>260:
            break
            
    bm.update(False)
    sc.update(False)
    g.show()   
    
status = Label(g, 20, 280, 160, 40, roboto18, WHITE)
progress = Label(g, 200, 280, 40, 40, roboto18, WHITE)

bm = BatteryMeter(g, getBatPercent, 350,10)
sc = smallClock(g,15,10)

secs = 0

def run():
    global mins,secs
    secs += 1
    g.fill_rect(XOFFSET+10,YOFFSET+79,int(3.66*secs),3,WHITE)
    g.show()
    if secs>=59 :
        draw_all()
        secs = 0

def app_init():
    global ticker
    sched.set_lightsleep(False)
    draw_title(False)
    bm.update(False)
    sc.update(True)
    connect(status,progress)
    draw_all()
    ticker = sched.setInterval(1000, run)

def app_end():
    global ticker
    if not ticker is None:
        sched.clearInterval(ticker)
        ticker = None
    sched.set_lightsleep(True)
    lazy_disconnect()
    g.fill(BLACK)

