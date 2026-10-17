from tempos import g,sched
from fonts import roboto18, roboto24, roboto36
import time
import png
from widgets import Label
from wifi import do_connected_action
import json
from requests import request
from config import OWP_KEY, LATITUDE, LONGTITUDE,summertime
from micropython import const

BLACK = const(0)
WHITE = const(1)

WX = const(205)
WY = (6)

status = Label(g, 0, 260, 100, 30, roboto18, WHITE)
progress = Label(g, 110, 260, 30, 30, roboto18, WHITE)

display = {
    "place": "xxx,CC",
    "desc": "description",
    "icon": "unknown",
    "temp": "00.0C",
    "humid": "00%",
    "press": "1000mb",
    "wind": "0.0mph S",
    "rise": "Sunrise 0:00",
    "set": "Sunset  0:00",
}

displayicon = png.getPNG("images/weather/unknown.png")


def deg_to_dir(d):
    dirs = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    dr = (d + 22) // 45
    if dr > 7:
        dr = 0
    return dirs[dr]


def secs_to_time(secs, zone):
    lsecs = secs + zone * 3600 + (3600 if summertime else 0) - 946684800
    loctime = time.gmtime(lsecs)
    return "{:2d}:{:02}".format(loctime[3], loctime[4])


def updateDisplay(dd):
    global displayicon
    display["place"] = dd["name"] + ", " + dd["sys"]["country"]
    display["desc"] = dd["weather"][0]["description"]
    if not (display["icon"] == dd["weather"][0]["icon"]):
        icon = dd["weather"][0]["icon"]
        displayicon = png.getPNG("images/weather/" + icon + ".png")
        display["icon"] = icon
    display["temp"] = "{:.1f} C".format(dd["main"]["temp"] - 273)
    display["humid"] = "{:d}%".format(dd["main"]["humidity"])
    display["press"] = "{:d}mb".format(dd["main"]["pressure"])
    display["wind"] = "{:.1f}mph {:s}".format(
        dd["wind"]["speed"], deg_to_dir(dd["wind"]["deg"])
    )
    display["rise"] = "Sunrise " + secs_to_time(dd["sys"]["sunrise"], dd["timezone"])
    display["set"] = "Sunset " + secs_to_time(dd["sys"]["sunset"], dd["timezone"])


def centre_text(str, font, x, y, c):
    global g
    g.setfont(font)
    g.setfontalign(0, -1)
    g.text(str, x, y, c)


def drawDisplay():
    global WX,WY
    CX = WX + (g.width - WX)//2
    g.fill_rect(WX, 0, g.width-WX, g.height, BLACK)
    png.drawPNG(g,displayicon, CX-48, WY+30)
    centre_text(display["place"], roboto24, CX, WY+9, WHITE)   
    centre_text(display["desc"], roboto18, CX, WY+125, WHITE)
    xoffset = CX-48
    wy = WY+90
    g.setfontalign(-1, -1)
    g.setfont(roboto36)
    g.text(display["temp"], xoffset, wy+60, WHITE)
    g.setfont(roboto18)
    g.text(display["humid"], xoffset, wy+95, WHITE)
    g.text(display["press"], xoffset, wy+115, WHITE)
    g.text(display["wind"], xoffset, wy+135, WHITE)
    g.text(display["rise"], xoffset, wy+160, WHITE)
    g.text(display["set"], xoffset, wy+180, WHITE)
    g.show()


def getupdate():
    loc = (LATITUDE, LONGTITUDE)
    url = "https://api.openweathermap.org/data/2.5/weather?lat={:.3f}&lon={:.3f}&appid={}".format(
        loc[0], loc[1], OWP_KEY
    )
    r = request("GET", url)
    dd = r.json()
    # 401 code: invalid api key
    if dd["cod"] == 200:
        try:
            updateDisplay(dd)
            drawDisplay()
        except Exception as err:
            status.update("{}:{}".format(dd["cod"], str(err)))
    else:
        print(dd)


def get_weather():
    global status, progress
    do_connected_action(getupdate, status, progress)



update = None


def app_init():
    global update
    g.fill_rect((g.width//2)-1,5,3,g.height-10,WHITE)
    drawDisplay()
    getupdate()
    update = sched.setInterval(600000,getupdate)


def app_end():
    global update
    if not update is None:
        sched.clearInterval(update)
        update = None
    g.fill(BLACK)
