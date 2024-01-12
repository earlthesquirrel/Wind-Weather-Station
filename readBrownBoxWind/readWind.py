import io
import serial


# Example lines of data
# Wind Speed: 0
# BMP Sensor: Temperature: 29.35 C Pressure: 96428 Pa Altitude: 415.91 m
# Wind Dir: 0
# DHT Sensor: Humidity: 27.00 Temperature: 78.62 F  Heat index: 77.45 F

global dht_humidity, dht_temp, dht_heat_index
global bmp_temp, bmp_altitude, bmp_pressure


def parse_data(data_line):
    splits = data_line.split(":")
    print(splits)

    if splits[0] == 'BMP Sensor':
        parse_bmp(splits)
    elif splits[0] == 'DHT Sensor':
        parse_dht(splits)
    elif splits[0].startswith('Wind'):
        parse_wind(splits)
    else:
        print("Unknown data type")


def parse_dht(input_data):
    print("dht data")
    global dht_humidity, dht_temp, dht_heat_index

    dht_humidity = float(input_data[2].split('T')[0])
    print(dht_humidity)
    dht_temp = float(input_data[3].split('F')[0])
    print(dht_temp)
    dht_heat_index = float(input_data[4].split('F')[0])
    print(dht_heat_index)


def parse_bmp(input_data):
    print("bmp data")
    global bmp_temp, bmp_altitude, bmp_pressure

    bmp_temp = float(input_data[2].split('C')[0])
    print(bmp_temp)
    bmp_pressure = int(input_data[3].split('A')[0])
    print(bmp_pressure)
    bmp_altitude = float(input_data[4])
    print(bmp_altitude)


def parse_wind(data):

    print("wind data")
    if data[0] == 'Wind Speed':
        wind_speed = int(data[1])
        print(wind_speed)
    elif data[0] == 'Wind Dir':
        wind_dir = int(data[1])
        print(wind_dir)


port = "/dev/cu.usbmodem14101"
baudrate = 115200

ser = serial.Serial(port, baudrate, timeout=1)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

while True:
    raw_data = str(sio.readline())
    print(raw_data)
    parse_data(raw_data)
    # sys.stdout.write(data)
    # sys.stdout.flush()
