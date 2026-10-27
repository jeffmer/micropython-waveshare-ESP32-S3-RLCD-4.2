from tempos import g,sched, getBatPercent
from fonts import roboto18, roboto24, roboto36, glcdfont
import time
import png
from widgets import Label, BatteryMeter, smallClock
from wifi import connect, lazy_disconnect
import json
from requests import request
from config import OWP_KEY, LATITUDE, LONGTITUDE,summertime
from micropython import const

BLACK = const(0)
WHITE = const(1)

WX = const(0)
WY = const(25)

ZONE = 0

status = Label(g, 0, 280, 100, 30, roboto18, WHITE)
progress = Label(g, 110, 280, 30, 30, roboto18, WHITE)

bm = BatteryMeter(g, getBatPercent, 350,10)
sc = smallClock(g,15,10)

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
smallicon = png.getPNG("images/weather36/unknown.png")


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
    global displayicon, ZONE
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
    ZONE = dd["timezone"]


def centre_text(str, font, x, y, c):
    global g
    g.setfont(font)
    g.setfontalign(0, -1)
    g.text(str, x, y, c)


def drawDisplay():
    global WX,WY
    g.fill(BLACK)
    png.drawPNG(g,displayicon, WX+48, WY+40)
    place = display["place"].split(",")[0]
    centre_text(place, roboto36, WX+100, WY+9, WHITE)   
    centre_text(display["desc"], roboto18, WX+100, WY+139, WHITE)
    g.setfontalign(-1, -1)
    xoffset = WX+240
    wy = WY+9
    g.setfont(roboto36)
    g.text(display["temp"], xoffset, wy, WHITE)
    g.setfont(roboto18)
    g.text(display["humid"], xoffset, wy+45, WHITE)
    g.text(display["press"], xoffset, wy+65, WHITE)
    g.text(display["wind"], xoffset, wy+85, WHITE)
    g.text(display["rise"], xoffset, wy+110, WHITE)
    g.text(display["set"], xoffset, wy+130, WHITE)
    g.fill_rect(200,WY+14,3,140,WHITE)
    g.fill_rect(20,195,360,3,WHITE)

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
        except Exception as err:
            status.update("{}:{}".format(dd["cod"], str(err)))
    else:
        print(dd)


def get_weather():
    global status, progress
    do_connected_action(getupdate, status, progress)


class Forecast:
    def __init__(self,x,y):
        self.x = x
        self.y = y 
        self.dt = ("00:00")
        self.temp = ("00C")
        self.icon = smallicon
        self.name = "unknown"
        self.desc = "weather description"

    def update(self,dt,temp,icon,desc):
        global ZONE
        self.dt = secs_to_time(dt,ZONE)
        self.temp = "{}C".format(round(temp - 273))
        if not (self.name == icon):
            self.name = icon
            self.icon = png.getPNG("images/weather36/" + self.name + ".png")
        self.desc = desc
      
    def draw(self):
        x = self.x
        y = self.y
        g.fill_rect(x,y,100,80,BLACK)
        g.setfontalign(-1,-1)
        g.setfont(roboto18)
        g.text(self.dt,x+5,y+5,WHITE)
        png.drawPNG(g,self.icon, x+5, y+20)
        g.text(self.temp,x+45,y+30)
        g.setfont(glcdfont)
        g.wordwraptext(self.desc,x+4,y+55,72,WHITE)

forecasts = []
for i in range(0,5):   
    forecasts.append(Forecast(i*80,205))

def updateForecast(dd):
    for i in range(0,5):
        forecasts[i].update(dd["list"][i]["dt"],
                            dd["list"][i]["main"]["temp"],
                            dd["list"][i]["weather"][0]["icon"],
                            dd["list"][i]["weather"][0]["description"],
                            )

def getForecast():
    global status
    loc = (LATITUDE, LONGTITUDE)
    url = "https://api.openweathermap.org/data/2.5/forecast?lat={:.3f}&lon={:.3f}&appid={}&cnt=5".format(
        loc[0], loc[1], OWP_KEY
    )
    r = request("GET", url)
    dd = r.json()
    try:
        updateForecast(dd)
    except Exception as err:
        status.update("{}:{}".format(dd["cod"], str(err)))



def drawAll():
    drawDisplay()
    for f in forecasts:
        f.draw()
    bm.update(False)
    sc.update(False)
    g.show()
    
def updateAll():
    connect(status,progress)
    getupdate()
    getForecast()
    lazy_disconnect()
    status.update("   ",False)
    
cycle = 0
def updateDraw():
    global cycle
    cycle += 1
    if cycle >= 30:
        print("updating")
        updateAll()
        drawAll()
        cycle = 0
    else:
        sc.update(True)
    
update = None

def app_init():
    drawAll()
    updateAll()
    drawAll()
    global update
    getupdate()
    update = sched.setInterval(20000,updateDraw)


def app_end():
    global update
    if not update is None:
        sched.clearInterval(update)
        update = None
    g.fill(BLACK)




