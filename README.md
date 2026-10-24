# micropython-waveshare-ESP32-S3-RLCD-4.2
Micropython based software for Waveshare's ESP32-S3-RLCD-4.2. Includes micropython driver for the ST7305 based 4.2 inch reflective LCD.


![Enclosure](pictures/enclosure.jpg)

**Note:** The refective LCD screen is quite fragile - I dropped my initial device a few inches onto a hard surface and it wrecked the screen - black splodges and random lines. I put the next one I bought into a protective enclosure made from clear perspex and brass spacers as pictured above. 


## Application Modules
The software contains the set of **apps** outlined below with screenshots. These apps are simply micropython modules that provide an `app_init()`and an `app_end()` method.The apps are supported by a version of **tempos** so installing a new app is simply a matter of copying it into the **apps** directory.  A full decription of **tempos** can be found in the repository `jeffmer/TTGO-T-watch-2020-Micropython-OS`. Clicking the Waveshare units user button **key** cycles through the available apps.

### Finder ###
<p align="center">
  <img src="pictures/finder.jpeg" />
</p>

### Clock app
<p align="center">
  <img src="pictures/clock.jpeg" />
</p>

### Bustimes app

### Weather app
<p align="center">
  <img src="pictures/weather.jpeg" />
</p>

### Planes app

<p align="center">
  <img src="pictures/planes.jpeg" />
</p>



## Power saving


## ST7305 driver


## Firmware

