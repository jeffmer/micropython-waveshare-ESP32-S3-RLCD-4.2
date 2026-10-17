from micropython import const
from tempos import g, rtc, sched, getBatPercent
from fonts import hugefont, roboto24, roboto36
from time import ticks_ms, ticks_diff
from widgets import BatteryMeter

BLACK = const(0)
WHITE = const(1)

X = 20

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

cycle = 9
bm = BatteryMeter(g, getBatPercent, 350,10)

def drawcolon(x,y):
    g.fill_rect(x,y,8,8, WHITE)
    g.fill_rect(x,y+25,8,8, WHITE)
    

def drawTime():
    global cycle
    g.fill_rect(0,25,g.width,g.height-25,BLACK)
    t = rtc.datetime()
    Y = 100
    g.setfontalign(-1, -1)
    g.setfont(hugefont)
    g.text("{:02}".format(t[4]), X, Y, WHITE)
    drawcolon(X+110,Y+20)
    g.text("{:02}".format(t[5]), X+130, Y, WHITE)
    drawcolon(X+240,Y+20)
    g.text("{:02}".format(t[6]), X+260, Y, WHITE)
    g.setfont(roboto36)
    g.setfontalign(0, -1)
    g.text("{}   {:02} {} {:02}".format(days[t[3]],t[1],months[t[1] - 1],t[0]),g.width//2,Y+100,WHITE)
    cycle+=1
    if cycle >=9:
        cycle=0
        bm.update(False)
    g.show()
  

ticker = None


def app_init():
    global ticker, cycle
    g.fill(BLACK)
    drawTime()
    ticker = sched.setInterval(1000, drawTime)


def app_end():
    sched.clearInterval(ticker)
    g.fill(BLACK)
