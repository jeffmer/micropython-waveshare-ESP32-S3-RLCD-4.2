import time
from micropython import const
from graphics import WHITE,BLACK
from fonts import roboto18, roboto24, roboto36
import math


class Label:
    "used to display text using a specific font, color and rectangle area"
    def __init__(self,g, x, y, w, h, font, c):
        self.g = g
        self.font = font
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c

    def update(self, str, now=True):
        self.g.setfont(self.font)
        self.g.fill_rect(self.x, self.y, self.w, self.h, WHITE if self.c==BLACK else BLACK)
        self.g.setfontalign(0, 0)
        self.g.text(str, self.x + self.w // 2, self.y + self.h // 2, self.c)
        if now:
            self.g.show()


class BatteryMeter:

    def __init__(self,g,getbat,x,y):
        self.g = g
        self.getbat = getbat
        self.x = x
        self.y = y

    def update(self, now = True):
        perc = self.getbat()
        self.g.fill_rect(self.x, self.y, 30, 14, BLACK)
        self.g.fill_rect(self.x + 2, self.y + 2, 26, 10, WHITE)
        self.g.fill_rect(self.x + 3, self.y + 3, math.ceil(25 * perc / 100), 8, BLACK)
        self.g.fill_rect(self.x + 30, self.y + 4, 3, 6, BLACK)
        if now:
            self.g.show()




