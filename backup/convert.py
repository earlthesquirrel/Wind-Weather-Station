import paho.mqtt.client as mqttClient
import time
import json

from wioREST import wioREST

def convertPressure( data, key ):
    if data != 'ERROR' :
        print (data[key]) 
        value = data[key] * 0.00029529983071445
        data[key] = value
        print (data[key])
        return data
     

# Here's where we poll and gather data.

#tempBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/temperature?access_token=6b6b1b39ebd90be742a1f2d285788c01'
#tempBME = wioREST(tempBME_URL)

pressureBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/pressure?access_token=6b6b1b39ebd90be742a1f2d285788c01'
pressureBME = wioREST(pressureBME_URL)
pressureBME = convertPressure(pressureBME, 'pressure')
