# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

from machine import Pin

key = Pin(18,Pin.IN)

if not key.value() == 0:  
    import loader



