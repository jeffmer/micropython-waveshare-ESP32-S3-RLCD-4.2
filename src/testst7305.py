import time
from machine import Pin, SPI
from drivers.st7305 import ST7305
from fonts import roboto24
from graphics import WHITE,BLACK
import png


txt = "The quick brown fox jumped over the lazy dog."

te = Pin(6, Pin.OUT, value = 1)
cs = Pin(40, Pin.OUT, value = 1)
dc = Pin(5, Pin.OUT, value = 1)
rs = Pin(41, Pin.OUT, value = 1)
spi = SPI(1, baudrate=40_000_000, polarity=0, phase=0, sck=Pin(11), mosi=Pin(12), miso=None)
g = ST7305(spi, cs, dc, rs)

g.fill(WHITE)
g.setfont(roboto24)
g.text('Hello, World', 10, 10, 1)

dialpic = png.getPNG("images/weather/11d.png")
t = time.ticks_ms()
png.drawPNG(g,dialpic, 100, 100)

g.show()
t = time.ticks_diff(time.ticks_ms(), t)
g.setfontalign(-1,-1)
g.text(f'Cost {t} ms.', 10, 40, 1)
g.show()
