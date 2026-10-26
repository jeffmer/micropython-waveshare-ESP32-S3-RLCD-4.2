from machine import Pin, SPI, I2C, RTC, Timer, lightsleep, wake_reason, SLEEP, ADC,PIN_WAKE
from scheduler import Scheduler
from graphics import WHITE, BLACK
from time import sleep, sleep_ms, ticks_us, ticks_diff, mktime, gmtime
from fonts import roboto18, roboto24,roboto36
import esp32
import micropython
import config
import wifi
from drivers.st7305 import ST7305
from drivers.pcf85063 import PCF85063
from drivers.switch import Switch
from widgets import Label
import ntptime


# lcd display
te = Pin(6, Pin.IN)
cs = Pin(40, Pin.OUT, value = 1)
dc = Pin(5, Pin.OUT, value = 1)
rs = Pin(41, Pin.OUT, value = 1)
spi = SPI(1, baudrate=40_000_000, polarity=0, phase=0, sck=Pin(11), mosi=Pin(12), miso=None)
g = ST7305(spi, cs, dc, rs)
g.fill(WHITE)
g.setfont(roboto36)
g.text('Loading....', 100, 100, 1)
g.show()

# persistent real time clock
I2C0 = I2C(0, scl=Pin(14), sda=Pin(13), freq=400000)
rtcp = Pin(15, Pin.IN)
prtc = PCF85063(I2C0, rtcp)  # GM time persistent clock
rtc = RTC()  # local clock

def set_local_time():
    dt = prtc.datetime()
    epoch_secs = mktime((dt[0], dt[1], dt[2], dt[4], dt[5], dt[6], dt[3], 0))
    tm = gmtime(
        epoch_secs + config.timezone * 3600 + (3600 if config.summertime else 0)
    )
    rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))

def do_ntp_sync():
    ntptime.settime()
    prtc.set_datetime(rtc.datetime())
    set_local_time()

# set up user button

key = Switch(18)

adc = ADC(4)

def getBatPercent():
    v = (adc.read_uv()/1000000)*3
    return int(((v-3.5)/0.7)*100)

sched = Scheduler()

# to deal with clock drift during lightsleep
sched.setInterval(600000,set_local_time) 







