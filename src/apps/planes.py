from micropython import const
from tempos import g, rtc, sched, getBatPercent
from wifi import connect, lazy_disconnect
from graphics import WHITE, BLACK
from widgets import Label, BatteryMeter, smallClock
from fonts import glcdfont, roboto24, roboto18
import array
import math
from time import ticks_ms, ticks_diff
from opensky import getupdate,pxAirPos,degtopx,CallSign, Country, Long, Lat, Alt, Landed, Speed, Heading, XOFFSET, YOFFSET
from config import AIRLONG, AIRLAT, AIRNAME
from adsbdb import getDetail
import machine


CR1 = const(115)
CR2 = const(70)
CR3 = const(35)
CX = const(150)
CY = const(150) 

def background():
    g.setcolor(WHITE)
    g.fill_rect(0,YOFFSET,270,270,WHITE)
    g.ellipse(CX, CY, CR1, CR1, BLACK, False)
    g.ellipse(CX, CY, CR2, CR2, BLACK, False)
    g.ellipse(CX, CY, CR3, CR3, BLACK, False)
    g.ellipse(CX, CY, 4,   4,   BLACK, False)

lastupdate =0
    

def drawAirport():
    x,y = degtopx(AIRLONG,AIRLAT)
    g.ellipse(x,y,4,4,BLACK,False)
    g.text(AIRNAME,x,y+14,BLACK)

def drawPlane(name,x, y, angle, alt, isselected):
    global shape
#    g.poly(x, y, array.array("h", [0,-7, 5, 7, -5, 7]), BLACK, not isselected, angle)
    g.poly(x, y, array.array("h", [1,-8, 1,-4, 8,0, 2,0, 1,5, 4,7, -4,7, -1,5, -1,0, -8,0, -1,-4, -1,-8]), BLACK, not isselected, angle)
    g.text(name,x,y+14,BLACK)
    g.text("{}m".format(int(alt)),x,y+24,BLACK)
    
selected = 0
current = -1
detail = None

def drawDetail(a):
    global selected, current, detail
    if current != selected:
        detail = getDetail(a[CallSign])
        current = selected   
    y = 80
    x = 335
    b,airline,fromloc,toloc = detail
    g.setcolor(BLACK)
    g.fill_rect(270,30,130,270,WHITE)
    g.setfontalign(0,0)
    g.setfont(roboto24)
    g.text(a[CallSign],x,y,BLACK)
    g.setfont(glcdfont)
    y=y+24
    g.text("ALT {} m".format(int(a[Alt])),x,y,BLACK)
    y=y+18
    g.text("SPD {} mph".format(int(a[Speed] * 2.237)),x,y,BLACK)
    y=y+18
    g.text("HDG {} deg".format(int(a[Heading])),x,y,BLACK)
    y=y+18
    if b:
        g.text("Airline: {}".format(airline),x,y,BLACK)
        y=y+18
        g.text("From: {}".format(fromloc),x,y,BLACK)
        y=y+18
        g.text("To: {}".format(toloc),x,y,BLACK)    
    g.poly(x, 50,
           array.array("h", [0,-10, 2,-9, 2,-5, 11,0, 3,0, 2,6, 5,9, -5,9, -2,6, -2,0, -11,0, -2,-5, -2,-9]),
           BLACK, False, math.radians(a[Heading])
           )
    g.show()

cycle = 0
selected = 0

def draw():
    global planes,cycle,lastupdate,selected
    g.setfont(glcdfont)
    g.setfontalign(0,0)
    now = ticks_ms()
    background()
    drawAirport()
    if cycle==0:
        lastupdate = ticks_ms()
        planes, selected = getupdate()
        drawDetail(planes[selected])
        bm.update(False)
        sc.update(False)
    dt = ticks_diff(now,lastupdate)/1000
    if planes:
        i=0
        for ac in planes:
            p = pxAirPos(ac,dt)
            if p[1]<265 and p[2]<265:
                drawPlane(p[0],p[1],p[2],p[3],p[4],i==selected)
            i = i + 1
    cycle+=1
    if cycle>=100:
        cycle=0
    g.show()
#    print("Draw time ",ticks_diff(ticks_ms(),now)," ms")

ticker = None

bm = BatteryMeter(g, getBatPercent, 350,10)
sc = smallClock(g,15,10)
status = Label(g, 20, 270, 160, 40, roboto18, BLACK)
progress = Label(g, 200, 270, 40, 40, roboto18, BLACK)


def app_init():
    global ticker,switch
    g.fill(WHITE)
    connect(status,progress)
    draw()
    ticker = sched.setInterval(250, draw)


def app_end():
    global ticker, planes, lastupdate
    planes = None
    lastupdate = 0
    sched.clearInterval(ticker)
    lazy_disconnect()
    g.fill(WHITE)