from machine import Pin
from scheduler import Event
from time import ticks_ms, ticks_diff
import esp32

PRESSED = 0
CLICK = 1
LONG_PRESS = 2
DOUBLE_CLICK = 3

class Switch(Event):
    def __init__(self, p):
        super().__init__()
        self.pin = Pin(p, Pin.IN)
        self.last_change = 0
        self.pin.irq(self.handler, Pin.IRQ_FALLING)
        esp32.wake_on_gpio([self.pin],esp32.WAKEUP_ALL_LOW)

    def handler(self, q):        
        if ticks_diff(ticks_ms(), self.last_change) > 60:
            self.irq_signal(CLICK)
        self.last_change = ticks_ms()
        

 
