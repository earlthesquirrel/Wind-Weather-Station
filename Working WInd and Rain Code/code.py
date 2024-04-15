from os import getenv
import board
import busio
import rtc
import keypad
import time
import asyncio
import countio
import collections

from digitalio import DigitalInOut
from analogio import AnalogIn
from adafruit_simplemath import map_range


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
#esp32_cs = DigitalInOut(board.D13)
#esp32_ready = DigitalInOut(board.D11)
#esp32_reset = DigitalInOut(board.D12)

esp32_cs = DigitalInOut(board.D10)
esp32_ready = DigitalInOut(board.D7)
esp32_reset = DigitalInOut(board.D5)

mqtt_broker = "69.109.130.206"
weather_feed = "weather/test"
mqtt_username = "power"
mqtt_password = "nD3M$3AhDob2K+xhAE"
mqtt_port = 1883;

lastWindDebounceTime = 0
windDebounceDelay = 1000

messageStartTime = 0
lastRainDebounceTime = 0
rainDebounceDelay = 500

anemometer =  board.D5 # The aneometer (wind speed) interrupt pin
windVane = AnalogIn(board.A0) # The nanalog pin used by wind vane
rainGauge = board.D11 # Tbe rain gauge interrupt pin

# Initial values for the measurements we report
wind_dir = 0.0
wind_speed = 0
compass_dir = 'N'

avg_dir_10m = 0
avg_speed_10m = 0
gust_10_min = 0
avg_compass_10m = 'N'

avg_dir_2m = 0
avg_speed_2m = 0
gust_2_min = 0
avg_compass_2m = 'N'

# Counters for how often interrrupts have triggered
windCount = 0
rainCount = 0


check_wind_sec = 3 # How frequently we check wind speed and wind direction, in seconds
queue_size = int( (10 * 60)/ check_wind_sec ) # For 10 minute interval, we have 10 min * 60 sec / check_wind_sec interval values.
wind_dir_10_min = collections.deque((),queue_size)
wind_speed_10_min = collections.deque((),queue_size)

check_rain_sec = 15 # How frequently we check rain amount, in seconds

spi = board.SPI()
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
print("Fetching text from", TEXT_URL)
r = requests.get(TEXT_URL)
print(r.text)
epochTime = int(r.text)
r.close()


compass = ["N  ","NNE","NE ","ENE","E  ","ESE","SE ","SSE","S  ","SSW","SW ","WSW","W  ","WNW","NW ","NNW","N  "]
rainFactor = 0.0161

print("Setting time")
print(time.time())

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print(f"Connected to Baugh.org. Listening for msgs")
    # Subscribe to all changes on the FEED_NAME.
    #client.subscribe(FEED_NAME)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Baugh.org.")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print(f"New message on topic {topic}: {message}")

MQTT.set_socket(socket, esp)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=mqtt_broker,
    port=mqtt_port,
    username=mqtt_username,
    password=mqtt_password
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

print("Connecting to MQTT Server...")
mqtt_client.connect()

def sendMqttMsg( message):
    mqtt_client.publish(weather_feed, message)



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

    global wind_dir_10_min
    global wind_speed_10_min

    global wind_dir_2_min
    global wind_speed_2_min

    global avg_dir_2m
    global avg_speed_2m
    global gust_2_min
    global avg_compass_2m

    global avg_dir_10m
    global avg_speed_10m
    global gust_10_min
    global avg_compass_10m


    # We need to see if we have 2 min and/or 10 min of data

    # We should have (10*60)/check_wind_sec values if we have 10 min of data
    ten_min = (10*60)/check_wind_sec
    # We should have (2*60)/check_wind_sec values if we have 2 min of data
    two_min = (2*60)/check_wind_sec
    # Both 2 min and 10 min are of interest.

    samples_dir = len(wind_dir_10_min)
    samples_speed = len(wind_speed_10_min)

    low_10_val = 300
    low_10_index = 0
    low_10_val = 300
    avg_dir_10m = 0
    avg_speed_10m = 0
    gust_10_min = 0

    low_index = 0
    high_10_val = 0
    high_10_index = 0
    high_2_val = 0
    high_2_index = 0
    avg_dir_2m = 0
    avg_speed_2m = 0
    gust_2_min = 0

    # From NWS - Gusts are reported when the peak wind speed reaches at least 16 knots (8.23111 m/s)
    # and the variation in wind speed between the peaks and lulls is at least 9 knots (4.63 m/s)
    # The duration of a gust is usually less than 20 sec

    if (samples_dir >= two_min and samples_speed >= two_min):
        print("In 2 min section")
        # We have 2 min worth of data
        index = 0
        for val in wind_speed_2_min[0:two_min]:
            print("in 2 min" + str(val))
            if val < low_2_val :
                low_2_val = val
            if val > high_2_val:
                high_2_val = val
                high_2_index = index
            avg_speed_2m = avg_speed_2m + val
            index+=1

        avg_speed_2m = avg_speed_2m / two_min

        if high_2_val >= low_2_val + 8.23111 :
            # This means we passed the first criteria
            if high_2_val + 4.63 > avg_speed_2m :
                # This means we passed the second criteria
                gust_2_min = high_2_val

        for val in wind_dir_2_min[0:two_min]:
            avg_dir_2m = avg_dir_2m + val

        avg_dir_2m = avg_dir_2m / two_min

        index = avg_dir_2m % 360
        index = int(round(index/ 22.5,0))
        avg_compass_2m = compass[index]

    else:
        return False

    if (samples_dir >= ten_min and samples_speed >= ten_min):
        print("In 10 min section")
        # We have 10 min worth of data
        index = 0
        for index, val in wind_speed_10_min[0:ten_min]:
            print("in 10 min" + str(val))
            if val < low_10_val :
                low_10_val = val
            if val > high_10_val:
                high_10_val = val
                high_10_index = index
            avg_speed_10m = avg_speed_10m + val
            index+=1

        avg_speed_10m = avg_speed_10m / ten_min

        if high_10_val >= low_10_val + 8.23111 :
            # This means we passed the first criteria
            if high_10_val + 4.63 > avg_speed_10m :
                # This means we passed the second criteria
                gust_10_min = high_10_val

        for val in wind_dir_10_min[0:ten_min]:
            avg_dir_10m = avg_dir_10m + val

        avg_dir_10m = avg_dir_10m / ten_min

        index = avg_dir_10m % 360
        index = int(round(index/ 22.5,0))
        avg_compass_10m = compass[index]
    else:
        return False



async def createMQTTMsg(delay):
    global compass_dir
    global wind_dir
    global wind_speed
    global rainCount

    oneMinStartTime = int(round(time.time() * 1000))
    twoMinStartTime = int(round(time.time() * 1000))
    tenMinStartTime = int(round(time.time() * 1000))

    rain_daily_amount = 0


    await asyncio.sleep(delay)

    while True:
        message = '{ "dateTime":'+str(time.time())+', "windDir":'+str(wind_dir)+', "windDirCmp":'+compass_dir+', "windSpeed":'+str(wind_speed)+' }'
        print(message)
        sendMqttMsg(message)

        intervalTimeCheck = int(round(time.time() * 1000 ))

        # Every 2 min
        if intervalTimeCheck > twoMinStartTime + ( 2 * 60 * 1000 ) :
            averageWindData()
            message = '{ "dateTime":'+str(time.time())+', "windDir2MinAvg":'+str(avg_dir_2m)+', "windDir2MinCmp":'+avg_compass_2m+', "windSpeed2MinAvg":'+str(avg_speed_2m)+', "windGust2Min":'+str(gust_2_min)+' }'
            print(message)
            sendMqttMsg(message)
            twoMinStartTime = intervalTimeCheck

        # Every 10 min
        if intervalTimeCheck > tenMinStartTime + ( 10 * 60 * 1000 ) :
            message = '{ "dateTime":'+str(time.time())+', "windDir10MinAvg":'+str(avg_dir_10m)+' , "windDir10MinCmp":'+avg_compass_10m+', "windSpeed10MinAvg":'+str(avg_speed_10m)+', "windGust10Min":'+str(gust_10_min)+' }'
            print(message)
            sendMqttMsg(message)
            tenMinStartTime = intervalTimeCheck

        # Every min
        if intervalTimeCheck > ( 1 * 60 * 1000 ) :
            rain_amount = rainCount * rainFactor
            rain_daily_amount = rain_daily_amount + rain_amount
            message = '{ "dateTime":'+str(time.time())+', "rain":'+str(rain_amount)+' }'
            rainCount = 0
            print(message)
            sendMqttMsg(message)
            oneMinStartTime = intervalTimeCheck


        await asyncio.sleep(delay)



async def catch_WindInterrupt(pin):
    global windCount
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                windCount = windCount+interrupt.count
                interrupt.count = 0
                #print("Wind interrupted!")
            # Let another task run.
            await asyncio.sleep(0)



"""
async def catch_RainInterrupt(pin):
    global rainCount
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                rainCount = rainCount+interrupt.count
                interrupt.count = 0
                print("Rain interrupted!")
            # Let another task run.
            await asyncio.sleep(0)

"""

async def catch_RainInterrupt(pin):
    """Print a message when pin goes low and when it goes high."""
    global rainCount
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    #print("pin went low")
                    rainCount = rainCount + 1
                #elif event.released:
                    #print("pin went high")
                    #rainCount = rainCount + 1
            await asyncio.sleep(0)




async def main():
    global check_wind_sec
    windInterrupt_task = asyncio.create_task(catch_WindInterrupt(anemometer))
    rainInterrupt_task = asyncio.create_task(catch_RainInterrupt(rainGauge))
    speed_task = asyncio.create_task(readWindSpeed(check_wind_sec))
    direction_task = asyncio.create_task(readWindDirection(check_wind_sec))
    mqtt_task = asyncio.create_task(createMQTTMsg(12))
    await asyncio.gather(windInterrupt_task, rainInterrupt_task, speed_task, direction_task)
    print("done")

asyncio.run(main())
