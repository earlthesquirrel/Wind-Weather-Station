#!/usr/bin/env python
#
# Earl's Wind and Rain sensor data gatherer
# Derrived from SDL example code (SDL_Pi_WeatherBoard and SDL_Pi_WeatherRack
# 
# Added MQTT code to send to weewx server
#

#import random 
#import binascii
#import struct
#import subprocess
#import smbus


import sys
import time
from datetime import datetime

import paho.mqtt.client as mqttClient
import json

import RPi.GPIO as GPIO

sys.path.append('./Adafruit_Python_GPIO')
sys.path.append('./SDL_Pi_TCA9545')
sys.path.append('../')

import Pi_WeatherRack as Pi_WeatherRack
from mqttREST import mqttREST

messenger = mqttREST("wind-1", "power", "nD3M$3AhDob2K+xhAE", 1883)


import SDL_Pi_TCA9545
#/*=========================================================================
#    I2C ADDRESS/BITS
#    -----------------------------------------------------------------------*/
TCA9545_ADDRESS =                         (0x73)    # 1110011 (A0+A1=VDD)
#/*=========================================================================*/

#/*=========================================================================
#    CONFIG REGISTER (R/W)
#    -----------------------------------------------------------------------*/
TCA9545_REG_CONFIG            =          (0x00)
#    /*---------------------------------------------------------------------*/

TCA9545_CONFIG_BUS0  =                (0x01)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS1  =                (0x02)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS2  =                (0x04)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS3  =                (0x08)  # 1 = enable, 0 = disable 

#/*=========================================================================*/

################
# Device Present State Variables
###############

#indicate interrupt has happened from as3936

as3935_Interrupt_Happened = False;

ADS1015_Present = False;
ADS1115_Present = False;

#############
# Test Function to see if sensors present
#############

def returnStatusLine(device, state):

	returnString = device
	if (state == True):
		returnString = returnString + ":   \t\tPresent" 
	else:
		returnString = returnString + ":   \t\tNot Present"
	return returnString


###############   
#
# WeatherRack Weather Sensors
#
# GPIO Numbering Mode GPIO.BCM
#

anemometerPin = 6
rainPin = 4

# constants

SDL_MODE_INTERNAL_AD = 0
SDL_MODE_I2C_ADS1015 = 1    # internally, the library checks for ADS1115 or ADS1015 if found

#sample mode means return immediately.  THe wind speed is averaged at sampleTime or when you ask, whichever is longer
SDL_MODE_SAMPLE = 0
#Delay mode means to wait for sampleTime and the average after that time.
SDL_MODE_DELAY = 1

weatherStation = Pi_WeatherRack.Pi_WeatherRack(anemometerPin, rainPin, 0,0, SDL_MODE_I2C_ADS1015)

weatherStation.setWindMode(SDL_MODE_SAMPLE, 5.0)

###############   

# Main Loop - sleeps 10 seconds
# Tests all I2C and WeatherRack devices on Weather Board 


# Main Program

print ("")
print ("Weather Board Driver -- Wind and Rain Only")
print ("")
print ("")
print ("Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S"))
print ("")



print ("----------------------")
print (returnStatusLine("ADS1015",weatherStation.ADS1015_Present))
print (returnStatusLine("ADS1115",weatherStation.ADS1115_Present))
print ("----------------------")

while True:

	print ("----------------- ")
	print (" WeatherRack Weather Sensors" )
	print (" WeatherRack Rain and Wind")
	print ("----------------- ")
	#
	print ("----------------- ")

	windSpeed = weatherStation.current_wind_speed()/1.6
	windGust = weatherStation.get_wind_gust()/1.6
	currentWindSpeed = "%0.2f" % windSpeed
	currentWindGust = "%0.2f" % windGust

	print ("Wind Speed=\t" + currentWindSpeed + " MPH")
	print ("MPH wind_gust=\t" + currentWindGust + " MPH")

	if (weatherStation.ADS1015_Present or weatherStation.ADS1115_Present):	
		currentWindDirection = "%0.2f" % weatherStation.current_wind_direction()
		print("Wind Direction=\t\t\t" + currentWindDirection)
		#print("Wind Direction=\t\t\t %0.2f Degrees" % weatherStation.current_wind_direction())
		#print("Wind Direction Voltage=\t\t %0.3f V" % weatherStation.current_wind_direction_voltage())

	print ("----------------- ")

	rain = weatherStation.get_current_rain_total();
	totalRain = "%0.2f" % rain
	print("Rain Total=\t"+totalRain+" in");


	epoch_time = int (time.time())
	message = '{"dateTime":'+str(epoch_time)+', "rain":'+totalRain+', "windDir":'+currentWindDirection+', "windSpeed": '+ currentWindSpeed+', "windGust": '+ currentWindGust+', "windGustDir":'+currentWindDirection+' }'
	print (message)

	messenger.send_msg(message)

	weatherStation.reset_rain_total()


	print ("----------------- ")

	time.sleep(5.0)
