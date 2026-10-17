from micropython import const
from tempos import g, rtc, sched, getBatPercent, set_local_time
from fonts import hugefont, roboto24, roboto36
from time import ticks_ms, ticks_diff
from widgets import BatteryMeter

BLACK = const(0)
WHITE = const(1)

X = 80

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

bm = BatteryMeter(g, getBatPercent, 100,50)

def drawcolon(x,y):
    g.fill_rect(x,y,8,8, WHITE)
    g.fill_rect(x,y+25,8,8, WHITE)
    
cycle = 0

def drawTime():
    global cycle
    cycle += 1
    if cycle >= 30:
        cycle = 0
        set_local_time()
    g.fill_rect(0,25,g.width,g.height-25,BLACK)
    t = rtc.datetime()
    Y = 100
    g.setfontalign(-1, -1)
    g.setfont(hugefont)
    g.text("{:02}".format(t[4]), X, Y, WHITE)
    drawcolon(X+110,Y+20)
    g.text("{:02}".format(t[5]), X+130, Y, WHITE)
    g.setfont(roboto36)
    g.setfontalign(0, -1)
    g.text("{}   {:02} {} {:02}".format(days[t[3]],t[1],months[t[1] - 1],t[0]),g.width//2,Y+100,WHITE)
    bm.update(False)
    g.show()
  
ticker = None

def app_init():
    global ticker, cycle
    g.fill(BLACK)
    drawTime()
    sched.set_lightsleep(True)
    ticker = sched.setInterval(20000, drawTime)


def app_end():
    global ticker
    sched.set_lightsleep(False)
    if not ticker is None:
        sched.clearInterval(ticker)
        ticker = None
    g.fill(BLACK)

