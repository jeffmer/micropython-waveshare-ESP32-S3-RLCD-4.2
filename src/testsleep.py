from tempos import g
from fonts import roboto24
from time import ticks_ms, ticks_diff
import machine

g.fill(0)
g.text("Sleep Test",20,20)
g.show()
start = ticks_ms()
g.text("ticks_ms {}".format(start),20,50)
g.show()
machine.lightsleep(2000)
stop = ticks_ms()
g.text("ticks_ms {} ticks_diff {} wake_reason".format(stop,ticks_diff(stop,start),machine.wake_reason()),20,80)
g.show


