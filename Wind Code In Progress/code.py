# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from os import getenv
import board
import busio
import rtc
import time
import asyncio
import countio
import collections

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

lastWindDebounceTime = 0
windDebounceDelay = 1000

lastRainDebounceTime = 0
rainDebounceDelay = 500

anemometer =  board.D5 # The aneometer (wind speed) interrupt pin
windVane = AnalogIn(board.A0) # The nanalog pin used by wind vane
rainGauge = board.D11 # Tbe rain gauge interrupt pin

# Initial values for the measurements we report
wind_dir = 0.0
wind_speed = 0
compass_dir = 'N'
windCount = 0
rainCount = 0


check_sec = 3 # How frequently we check wind speed and wind direction
queue_size = int( (10 * 60)/ check_sec ) # For 10 minute interval, we have 10 min * 60 sec / check_sec interval values.
wind_dir_10_min = collections.deque((),queue_size)
wind_speed_10_min = collections.deque((),queue_size)

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
rainFactor = 0.0161

print("Setting time")
print(time.time())

async def readRainAmount(delay):
    global lastRainDebounceTime
    global rainDebounceDelay
    global rainCount
    global rainAmount

    await asyncio.sleep(delay)

    while True:
        milli_sec = int(round(time.time() * 1000))
        if ((milli_sec - lastRainDebounceTime) > rainDebounceDelay):
            lastRainDebounceTime = milli_sec
            rainCount = 0
            rainAmount = rainCount * rainFactor
        await asyncio.sleep(delay)



async def readWindDirection(delay):
    global wind_dir
    global compass_dir
    global wind_dir_10_min

    await asyncio.sleep(delay)

    while True:
        #print("windVane raw "+str(windVane.value))
        wind_dir = map_range(windVane.value, float(0), float(60046), float(0), float(360))
        wind_dir_10_min.append(wind_dir)

        #print("wind dir ="+str(wind_dir))
        index = wind_dir % 360
        index = int(round(index/ 22.5,0))
        #print("index="+str(index))
        compass_dir = compass[index]
        #print("compass Dir="+str(compass_dir))
        await asyncio.sleep(delay)


async def readWindSpeed(delay):
    global windCount
    global lastWindDebounceTime
    global windDebounceDelay
    global wind_speed
    global wind_speed_10_min

    await asyncio.sleep(delay)

    while True:
        milli_sec = int(round(time.time() * 1000))
        if ((milli_sec - lastWindDebounceTime) > windDebounceDelay):
            lastWindDebounceTime = milli_sec

            # Sensor Resolution is 0.0875 m/s
            # 1 Round in 1 Sec = 20 pulses, Wind Speed = 1.75 m/s
            # 4.5 Round in 1 Sec = 90 pulses, Wind Speed = 7.875 m/s

            wind_speed = windCount * 8.75 * 0.01;
            wind_speed  = wind_speed * 2.2369 # Converting from m/s to miles/hour
            wind_speed_10_min.append(wind_speed)
            #print("Wind Speed: "+str(wind_speed)+" m/s")  # in m/s
            count = 0
        await asyncio.sleep(delay)



async def averageWindData():
    # We need to see if we have 2 min and/or 10 min of data
    global wind_dir_10_min
    global wind_speed_10_min

    # We should have (10*60)/check_sec values if we have 10 min of data
    ten_min = (10*60)/check_sec
    # We should have (2*60)/check_sec values if we have 2 min of data
    two_min = (2*60)/check_sec
    # Both 2 min and 10 min are of interest.

    samples_dir = len(wind_dir_10_min)
    samples_speed = len(wind_speed_10_min)

    low_10_val = 300
    low_10_index = 0
    low_10_val = 300
    avg_dir_10 = 0
    avg_speed_10 = 0
    gust_10_min = 0

    low_index = 0
    high_10_val = 0
    high_10_index = 0
    high_2_val = 0
    high_2_index = 0
    avg_dir_2 = 0
    avg_speed_2 = 0
    gust_2_min = 0

    # From NWS - Gusts are reported when the peak wind speed reaches at least 16 knots (8.23111 m/s)
    # and the variation in wind speed between the peaks and lulls is at least 9 knots (4.63 m/s)
    # The duration of a gust is usually less than 20 sec

    if (samples_dir >= two_min and samples_speed >= two_min):
        # We have 2 min worth of data
        index = 0
        for val in wind_speed_10_min[0:two_min]:
            if val < low_2_val :
                low_2_val = val
            if val > high_2_val:
                high_2_val = val
                high_2_index = index
            avg_speed_2 = avg_speed_2 + val
            index+=1

        avg_speed_2 = avg_speed_2 / two_min

        if high_2_val >= low_2_val + 8.23111 :
            # This means we passed the first criteria
            if high_2_val + 4.63 > avg_speed_2 :
                # This means we passed the second criteria
                gust_2_min = high_2_val

        for val in wind_dir_2_min[0:two_min]:
            avg_dir_2 = avg_dir_2 + val

        avg_dir_2 = avg_dir_2 / two_min
    else:
        return False

    if (samples_dir >= ten_min and samples_speed >= ten_min):
        # We have 10 min worth of data
        index = 0
        for index, val in wind_speed_10_min[0:ten_min]:
            if val < low_10_val :
                low_10_val = val
            if val > high_10_val:
                high_10_val = val
                high_10_index = index
            avg_speed_10 = avg_speed_10 + val
            index+=1

        avg_speed_10 = avg_speed_10 / ten_min

        if high_10_val >= low_10_val + 8.23111 :
            # This means we passed the first criteria
            if high_10_val + 4.63 > avg_speed_10 :
                # This means we passed the second criteria
                gust_10_min = high_10_val

        for val in wind_dir_10_min[0:ten_min]:
            avg_dir_10 = avg_dir_10 + val

        avg_dir_10 = avg_dir_10 / ten_min
    else:
        return False



async def createMQTTMsg(delay):
    global compass_dir
    global wind_dir
    global wind_speed

    await asyncio.sleep(delay)

    while True:
        message = '{ "dateTime":'+str(time.time())+', "wind_dir degrees":'+str(wind_dir)+' , "wind_dir compass":'+compass_dir+' , "wind_speed":'+str(wind_speed)+' }'
        print(message)
        await asyncio.sleep(delay)



async def catch_WindInterrupt(pin):
    global count
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                windCount = windCount+interrupt.count
                interrupt.count = 0
                #print("interrupted!")
            # Let another task run.
            await asyncio.sleep(0)



async def catch_RainInterrupt(pin):
    global rainCount
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                rainCount = rainCount+interrupt.count
                interrupt.count = 0
                #print("interrupted!")
            # Let another task run.
            await asyncio.sleep(0)



async def main():
    global check_sec
    windInterrupt_task = asyncio.create_task(catch_WindInterrupt(anemometer))
    rainInterrupt_task = asyncio.create_task(catch_RainInterrupt(rainGauge))
    speed_task = asyncio.create_task(readWindSpeed(check_sec))
    direction_task = asyncio.create_task(readWindDirection(check_sec))
    average_task = asyncio.create_task(averageWindData())
    mqtt_task = asyncio.create_task(createMQTTMsg(12))
    await asyncio.gather(windInterrupt_task,rainInterrupt_task, speed_task, direction_task)
    print("done")

asyncio.run(main())



