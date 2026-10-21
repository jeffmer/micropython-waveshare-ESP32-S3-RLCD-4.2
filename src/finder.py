from tempos import g, getBatPercent,key,sched
from loader import appRing
import png
from fonts import roboto18, roboto36, glcdfont
from widgets import BatteryMeter, smallClock

names = appRing.names
icons = []

bm = BatteryMeter(g, getBatPercent, 350,10)
sc = smallClock(g,15,10)

BLACK = const(1)
WHITE = const(0)

for n in names:
    icons.append(png.getPNG("images/icons/" + n + ".png"))

selected = 1
in_app = False

def draw():
    global selected
    x = 31
    y = 110
    g.fill_rect(0,50,400,200,WHITE)
    g.setfont(roboto36)
    g.setfontalign(0,-1)
    g.text("InfoGlance",200,55)
    g.setfont(roboto18)
    for i in range(0,len(names)):
        png.drawPNG(g,icons[i], x+14, y)
        g.text(names[i], x+46,y+70,BLACK)
        if i == selected:
            g.rect(x+7,y-2,78,92,BLACK)
        x+=82
    g.show()

ticker = None

def draw_widgets():
    sc.update(False)
    bm.update(True)

def app_init():
    global ticker
    g.fill(WHITE)
    sc.update(False)
    bm.update(False)
    g.setfont(glcdfont)
    g.setfontalign(0,-1)
    g.text("Double click on selected app to run it.",200,284)
    draw()
    ticker = sched.setInterval(20000,draw_widgets)

def app_end():
    global ticker
    g.fill(WHITE)
    if ticker is not None:
        sched.clearInterval(ticker)
        ticker = None

def enter_app():
    global selected, in_app
    if selected<0 or selected>=len(names):
        return
    else:
        app_end()
        in_app=True
        appRing.setCurrent(selected)
        appRing.begin()

def exit_app():
    global in_app
    if in_app:
        appRing.end()
        in_app = False
        app_init()

def next_app():
    global selected,dclto
    dclto = None
    selected+=1
    if selected >= len(names):
        selected = -1
    draw()

    
dclto = None # double click TO

def select(v):
    global selected, in_app, dclto
    if in_app:
        exit_app()
    elif not dclto is None:
        sched.clearTimeout(dclto)
        dclto = None
        enter_app()
    else:
        dclto = sched.setTimeout(400, next_app)
        
def _safecall(v):
    sched.setTimeout(10, select, v)
    
key.addListener(_safecall)
