from micropython import const
from tempos import g, rtc, sched, getBatPercent, set_local_time
from fonts import roboto18, roboto24
from time import ticks_ms, ticks_diff
from widgets import Label, BatteryMeter, smallClock
import math
import array
import wifi
from requests import request

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

class Joke():

    X = const(170)
    Y = const(80)
    W = const(210)
    D = const(6000)

    def __init__(self,st,pl):
        self.setup = st
        self.punchline = pl
        self.timer = None

    def drawpunchline(self,y):
        g.setfontalign(-1,-1)
        g.setfont(roboto18)
        g.wordwraptext(self.punchline,self.X,y,self.W,WHITE)
        self.timer = None
        g.show()

    def draw(self):
        g.setfontalign(-1,-1)
        g.setfont(roboto18)
        py = g.wordwraptext(self.setup,self.X,self.Y,self.W,WHITE)       
        py += roboto18.height()
        self.timer = sched.setTimeout(self.D, self.drawpunchline, py)

    def cancel(self):
        if not self.timer is None:
            sched.clearTimeout(self.timer)

jokes = []
njoke = 0
NJOKES = const(20)
currentjoke = 0

def getjokes():
    global jokes, njoke, NJOKES
    jokes = []
    r = request("GET", "https://official-joke-api.appspot.com/jokes/random/{}".format(NJOKES))
    dd = r.json()
    for i in range(0,NJOKES):
        jokes.append(Joke(dd[i]["setup"],dd[i]["punchline"]))


status = Label(g, 20, 260, 160, 40, roboto18, WHITE)
progress = Label(g, 200, 260, 40, 40, roboto18, WHITE)
bm = BatteryMeter(g, getBatPercent, 350,10)
sc = smallClock(g,15,10)
cf = ClockFace(80,120,66)

cycle = 20

def drawAll(b=True):
    global jokes,currentjoke, NJOKES, status, progress, cycle
    cycle += 1
    if b and cycle >= 20:
        cycle = 0
        wifi.do_connected_action(getjokes,status,progress)
    g.fill(BLACK)
    t = rtc.datetime()
    cf.draw(t[4],t[5])
    if len(jokes)>0:
        currentjoke = (currentjoke+1) % NJOKES  
        jokes[currentjoke].draw()
    g.setfont(roboto24)
    g.setfontalign(0,0)
    g.text(days[t[3]],80,220,WHITE)
    g.text("{} {:02}".format(months[t[1] - 1],t[2]),80,250,WHITE)
    bm.update(False)
    sc.update(False)
    if b:
        g.show()
 
ticker = None
        
def app_init():
    g.fill(BLACK)
    drawAll(False)

def app_start():
    global ticker
    if len(jokes)==0:
        drawAll()
    ticker = sched.setInterval(30000, drawAll)

def app_end():
    global ticker, jokes, currentjoke
    jokes[currentjoke].cancel()
    sched.clearInterval(ticker)
    ticker = None

