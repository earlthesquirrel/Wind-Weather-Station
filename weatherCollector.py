import paho.mqtt.client as mqttClient
import time
import json

from wioREST import wioREST

 
Connected = False   #global variable for the state of the connection


def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
        print("Connected to broker")
 
        global Connected                #Use global variable
        Connected = True                #Signal connection 
 
    else:
        print("Connection failed")
 

def build_msg(measurement):

    epoch_time = int (time.time())
    # message = '{"dateTime":'+str(epoch_time)+',"outTemp":'+str(32.2)+'}'
    global message
    message = '{"dateTime":'+str(epoch_time)+','+measurement+'}'
    
    return message


def send_msg(value):

    broker_address= "172.16.0.4"
    port = 1883
    user = "power"
    password = "nD3M$3AhDob2K+xhAE"
 
    client = mqttClient.Client("Python")               #create new instance
    client.username_pw_set(user, password=password)    #set username and password
    client.on_connect= on_connect                      #attach function to callback
    client.connect(broker_address, port=port)          #connect to broker
    client.publish("weather",value)
    client.disconnect()

def build_and_send_msg(data, key, label):
    if  data != 'ERROR':
        #print data
        #print (data[key])
	if data is not None:
       	   if data[key] is not None:
              msg = build_msg('"'+label+'":'+str(data[key]))
              send_msg(msg)
   
def convertPressure( data, key ):
    if data != 'ERROR' :
        if data[key] is not None:
           #print (data[key])
           value = data[key] * 0.00029529983071445
           data[key] = value
           #print (data[key])
        return data

def convertTemperature( data, key ):
    if data != 'ERROR' :
        if data[key] is not None:
            #print (data[key])
            value = ( data[key] * 9/5) + 32
            data[key] = value
            #print (data[key])
        return data

def convertMetersToFeet( data, key ):
    if data != 'ERROR' :
        if data[key] is not None:
            #print (data[key])
            value = data[key] * 3.2808
            data[key] = value
            #print (data[key])
        return data

# Here's where we poll and gather data.

altitudeBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/altitude?access_token=6b6b1b39ebd90be742a1f2d285788c01'
altitudeBME = wioREST(altitudeBME_URL)
altitudeBME = convertMetersToFeet(altitudeBME, 'altitude')
build_and_send_msg(altitudeBME, 'altitude', 'altimeter')

tempBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/temperature?access_token=6b6b1b39ebd90be742a1f2d285788c01'
tempBME = wioREST(tempBME_URL)
tempBME = convertTemperature(tempBME, 'temperature')
build_and_send_msg(tempBME, 'temperature', 'outTemp')

humidityBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/humidity?access_token=6b6b1b39ebd90be742a1f2d285788c01'
humidityBME = wioREST(humidityBME_URL)
build_and_send_msg(humidityBME, 'humidity', 'outHumidity')

pressureBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/pressure?access_token=6b6b1b39ebd90be742a1f2d285788c01'
pressureBME = wioREST(pressureBME_URL)
pressureBME = convertPressure(pressureBME, 'pressure')
build_and_send_msg(pressureBME, 'pressure', 'barometer')

dust_URL = 'https://us.wio.seeed.io/v1/node/GroveDustD1/dust?access_token=da61a02b1808e7c4bd2965b75d4ca863'
dust = wioREST(dust_URL)
build_and_send_msg(dust, 'dust', 'pm1_0')

C2H5OH_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C2H5OH?access_token=da61a02b1808e7c4bd2965b75d4ca863'
C2H5OH = wioREST(C2H5OH_URL)
build_and_send_msg(C2H5OH, 'concentration_ppm', 'c2h5oh')

C3H8_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C3H8?access_token=da61a02b1808e7c4bd2965b75d4ca863'
C3H8 = wioREST(C3H8_URL)
build_and_send_msg(C3H8, 'concentration_ppm', 'c3h8')

C4H10_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C4H10?access_token=da61a02b1808e7c4bd2965b75d4ca863'
C4H10 = wioREST(C4H10_URL)
build_and_send_msg(C4H10, 'concentration_ppm', 'c4h10')

CH4_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/CH4?access_token=da61a02b1808e7c4bd2965b75d4ca863'
CH4 = wioREST(CH4_URL)
build_and_send_msg(CH4, 'concentration_ppm', 'ch4')

CO_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/CO?access_token=da61a02b1808e7c4bd2965b75d4ca863'
CO = wioREST(CO_URL)
build_and_send_msg(CO, 'concentration_ppm', 'co')

H2_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/H2?access_token=da61a02b1808e7c4bd2965b75d4ca863'
H2 = wioREST(H2_URL)
build_and_send_msg(H2, 'concentration_ppm', 'h2')

NH3_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/NH3?access_token=da61a02b1808e7c4bd2965b75d4ca863'
NH3 = wioREST(NH3_URL)
build_and_send_msg(NH3, 'concentration_ppm', 'nh3')

NO2_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/NO2?access_token=da61a02b1808e7c4bd2965b75d4ca863'
NO2 = wioREST(NO2_URL)
build_and_send_msg(NO2, 'concentration_ppm', 'no2')

humiditySHT_URL = 'https://us.wio.seeed.io/v1/node/GroveTempHumiSHT31I2C0/humidity?access_token=d5c417d04b21aaa4683c0f99c711532a'
humiditySHT = wioREST(humiditySHT_URL)
build_and_send_msg(humiditySHT, 'humidity', 'extraHumid1')

tempSHT_URL = 'https://us.wio.seeed.io/v1/node/GroveTempHumiSHT31I2C0/temperature?access_token=d5c417d04b21aaa4683c0f99c711532a'
tempSHT = wioREST(tempSHT_URL)
tempSHT = convertTemperature(tempSHT, 'temperature')
build_and_send_msg(tempSHT, 'temperature', 'extraTemp1')


