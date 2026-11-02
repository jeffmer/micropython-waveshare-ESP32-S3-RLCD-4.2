from micropython import const
from tempos import g, rtc, sched, getBatPercent, set_local_time
from fonts import hugefont, roboto24, roboto36
from time import ticks_ms, ticks_diff
from widgets import BatteryMeter
import math
import array

BLACK = const(0)
WHITE = const(1)

days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
months = [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
]

class ClockFace():
    def __init__(self, x,y,r):
        self.x = x
        self.y = y
        self.r = r

    def drawRotRect(self, w, r1, r2, angle):
        w2, ll, a = w // 2, r2 - r1, (angle + 270) * (math.pi / 180)
        coord = array.array("h", [0, -w2, ll, -w2, ll, w2, 0, w2])
        x, y = math.ceil(self.x + r1 * math.cos(a)), math.ceil(
            self.y + r1 * math.sin(a)
        )
        g.poly(x, y, coord, WHITE , True, a)

    def draw(self, hrs,mins,now=False):
        g.ellipse(self.x, self.y, self.r, self.r, WHITE, True)
        g.ellipse(self.x, self.y, self.r-6, self.r-6, BLACK, True)
        for i in range(0,4):
            self.drawRotRect(6,self.r-14,self.r-6,i*90)   
        #hour hand
        self.drawRotRect(6, 0, self.r-25, hrs * 30 + mins // 2)
        #minute hand
        self.drawRotRect(4, 0, self.r-15, mins*6)
        g.ellipse(self.x, self.y, 8, 8, WHITE, True)

bm = BatteryMeter(g, getBatPercent, 350,10)
cf = ClockFace(200,90,66)

def drawcolon(x,y):
    g.fill_rect(x,y,8,8, WHITE)
    g.fill_rect(x,y+25,8,8, WHITE)

def drawTime():
    X = 85
    g.fill(BLACK)
    t = rtc.datetime()
    cf.draw(t[4],t[5])
    Y = 170
    g.setfontalign(-1, -1)
    g.setfont(hugefont)
    g.text("{:02}".format(t[4]), X, Y, WHITE)
    drawcolon(X+110,Y+20)
    g.text("{:02}".format(t[5]), X+130, Y, WHITE)
    g.setfont(roboto24)
    g.setfontalign(0,0)
    g.text("{}   {} {:02}".format(days[t[3]], months[t[1] - 1],t[2]),200,270,WHITE)
    bm.update(False)
    g.show()
 
ticker = None

def app_init():
    global ticker, cycle
    g.fill(BLACK)
    drawTime()
    ticker = sched.setInterval(20000, drawTime)

def app_end():
    global ticker
    if not ticker is None:
        sched.clearInterval(ticker)
        ticker = None
    g.fill(BLACK)
