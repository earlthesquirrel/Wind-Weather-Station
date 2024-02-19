# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from os import getenv
import board
import busio
import rtc
import time
import asyncio
import countio

from digitalio import DigitalInOut
from analogio import AnalogIn
from adafruit_simplemath import map_range

'''
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi

# Get wifi details and more from a settings.toml file
# tokens used by this Demo: CIRCUITPY_WIFI_SSID, CIRCUITPY_WIFI_PASSWORD
secrets = {
    "ssid": getenv("CIRCUITPY_WIFI_SSID"),
    "password": getenv("CIRCUITPY_WIFI_PASSWORD"),
}
if secrets == {"ssid": None, "password": None}:
    try:
        # Fallback on secrets.py until depreciation is over and option is removed
         from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in settings.toml, please add them there!")
        raise


# If you have an AirLift Featherwing or ItsyBitsy Airlift:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

#const char *mqtt_broker = "69.109.130.206";
#const char *topic = "weather/test";
#const char *mqtt_username = "power";
#const char *mqtt_password = "nD3M$3AhDob2K+xhAE";
#const int mqtt_port = 1883;
'''

lastDebounceTime = 0
debounceDelay = 1000

anemometer =  board.D5 # The aneometer (wind speed) interrupt pin
windVane = AnalogIn(board.A0) # The nanalog pin used by wind vane

# Initial values for the measurements we report
wind_dir = 0.0
wind_speed = 0
compass_dir = 'N'
count = 0

'''
# Secondary (SCK1) SPI used to connect to WiFi board on Arduino Nano Connect RP2040
if "SCK1" in dir(board):
    spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
else:
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

#for ap in esp.scan_networks():
#    print("\t%s\t\tRSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except OSError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))

TEXT_URL = "https://io.adafruit.com/api/v2/time/seconds?x-aio-key=5e2a8804feafe7214cd3711c5138a2f2a02b4414&tz=UTC"

# esp._debug = True
'''
# Get Time sync'ed with a global baseline
rtclock = rtc.RTC()
'''
print("Fetching text from", TEXT_URL)
r = requests.get(TEXT_URL)
print(r.text)
rtclock.datetime = time.localtime(int(r.text))
r.close()

'''
rtclock.datetime = time.localtime(int(1707505760))

compass = ["N  ","NNE","NE ","ENE","E  ","ESE","SE ","SSE","S  ","SSW","SW ","WSW","W  ","WNW","NW ","NNW","N  "]

print("Setting time")
print(time.time())


async def readWindDirection(delay):
    global wind_dir
    global compass_dir

    await asyncio.sleep(delay)

    while True:
        #print("windVane raw "+str(windVane.value))
        wind_dir = map_range(windVane.value, float(0), float(60046), float(0), float(360))
        #print("wind dir ="+str(wind_dir))
        index = wind_dir % 360
        index = int(round(index/ 22.5,0))
        #print("index="+str(index))
        compass_dir = compass[index]
        #print("compass Dir="+str(compass_dir))
        await asyncio.sleep(delay)


async def readWindSpeed(delay):
    global count
    global lastDebounceTime
    global debounceDelay
    global wind_speed

    await asyncio.sleep(delay)

    while True:
        milli_sec = int(round(time.time() * 1000))
        if ((milli_sec - lastDebounceTime) > debounceDelay):
            lastDebounceTime = milli_sec
            wind_speed = count * 8.75 * 0.01;
            #print("Wind Speed: "+str(wind_speed)+" m/s")  # in m/s
            count = 0
        await asyncio.sleep(delay)



async def createMQTTMsg(delay):
    global compass_dir
    global wind_dir
    global wind_speed

    await asyncio.sleep(delay)

    while True:
        message = '{ "dateTime":'+str(time.time())+', "wind_dir degrees":'+str(wind_dir)+' , "wind_dir compass":'+compass_dir+' , "wind_speed":'+str(wind_speed)+' }'
        print(message)
        await asyncio.sleep(delay)



async def catch_interrupt(pin):
    global count
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                count = count+interrupt.count
                interrupt.count = 0
                #print("interrupted!")
            # Let another task run.
            await asyncio.sleep(0)


async def main():
    interrupt_task = asyncio.create_task(catch_interrupt(anemometer))
    speed_task = asyncio.create_task(readWindSpeed(3))
    direction_task = asyncio.create_task(readWindDirection(3))
    mqtt_task = asyncio.create_task(createMQTTMsg(12))
    await asyncio.gather(interrupt_task, speed_task, direction_task)
    print("done")

asyncio.run(main())



