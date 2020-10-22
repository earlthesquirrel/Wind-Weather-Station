import paho.mqtt.client as mqttClient
import time
import json

from mqttREST import mqttREST

messenger = mqttREST("power", "nD3M$3AhDob2K+xhAE", 1883)


# Here's where we poll and gather data.

altitudeBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/altitude?access_token=6b6b1b39ebd90be742a1f2d285788c01'
altitudeBME = messenger.wioRESTcall(altitudeBME_URL)
altitudeBME = messenger.convertMetersToFeet(altitudeBME, 'altitude')
messenger.build_and_send_msg(altitudeBME, 'altitude', 'altimeter')

tempBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/temperature?access_token=6b6b1b39ebd90be742a1f2d285788c01'
tempBME = messenger.wioRESTcall(tempBME_URL)
tempB = messenger.getValue(tempBME, 'temperature')
tempBME = messenger.convertTemperature(tempBME, 'temperature')
if tempBME != 8888 and tempBME != 9999:
     	# messenger.build_and_send_msg(tempBME, 'temperature', 'outTemp')
     	messenger.build_and_send_msg(tempBME, 'temperature', 'extraTemp1')
else:
	print("TempBME read error", tempBME)

humidityBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/humidity?access_token=6b6b1b39ebd90be742a1f2d285788c01'
humidityBME = messenger.wioRESTcall(humidityBME_URL)
#messenger.build_and_send_msg(humidityBME, 'humidity', 'outHumidity')
messenger.build_and_send_msg(humidityBME, 'humidity', 'extraHumid1')

pressureBME_URL = 'https://us.wio.seeed.io/v1/node/GroveBME280I2C1/pressure?access_token=6b6b1b39ebd90be742a1f2d285788c01'
pressureBME = messenger.wioRESTcall(pressureBME_URL)
pressureB = messenger.getValue(pressureBME, 'pressure')
pressureBME = messenger.convertPressure(pressureBME, 'pressure')
messenger.build_and_send_msg(pressureBME, 'pressure', 'pressure')

try:
	# Here we calculate barometric pressure -- which is pressure corrected to sea level
	pressureB = pressureB/100.0
	altitudeB = 360 # Altitude of house doesn't change... or at least not unless earthquake :-) 
	#print ("pressure ", pressureB )
	#print ("altitude ", altitudeB )
	#print ("tempB ", tempB)
	barometric = (pressureB * pow( 1 - ( 0.0065*altitudeB ) / (tempB + (0.0065*altitudeB) +273.15), -5.257))/33.8639
	#print("barometric is ", barometric)
	messenger.build_and_send_msg_with_data(barometric,'barometer')
except TypeError:
	print("Error calculating sea level barometric pressure, one variable is pprobably undefined");

tempCO2_URL = 'https://us.wio.seeed.io/v1/node/GroveCo2MhZ16UART0/temperature?access_token=6b6b1b39ebd90be742a1f2d285788c01'
tempCO2 = messenger.wioRESTcall(tempCO2_URL)
tempCO2 = messenger.convertTemperature(tempCO2, 'temperature')
if tempCO2 != 8888 and tempCO2 != 9999:
	 messenger.build_and_send_msg(tempCO2, 'temperature', 'extraTemp3')
else:
	print("TempCO2 read error", tempCO2)

humiditySHT35_URL = 'https://us.wio.seeed.io/v1/node/GroveTempHumiSHT35I2C0/humidity?access_token=d5c417d04b21aaa4683c0f99c711532a'
humiditySHT35 = messenger.wioRESTcall(humiditySHT35_URL)
messenger.build_and_send_msg(humiditySHT35, 'humidity', 'outHumidity')

tempSHT35_URL = 'https://us.wio.seeed.io/v1/node/GroveTempHumiSHT35I2C0/temperature?access_token=d5c417d04b21aaa4683c0f99c711532a'
tempSHT35 = messenger.wioRESTcall(tempSHT35_URL)
tempSHT35 = messenger.convertTemperature(tempSHT35, 'temperature')
if tempSHT35 != 8888 and tempSHT35 != 9999:
	messenger.build_and_send_msg(tempSHT35, 'temperature', 'outTemp')
else:
	print("TempSHT35 read error", tempSHT35)

dust_URL = 'https://us.wio.seeed.io/v1/node/GroveDustD1/dust?access_token=da61a02b1808e7c4bd2965b75d4ca863'
dust = messenger.wioRESTcall(dust_URL)
messenger.build_and_send_msg(dust, 'dust', 'pm1_0')

C2H5OH_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C2H5OH?access_token=da61a02b1808e7c4bd2965b75d4ca863'
C2H5OH = messenger.wioRESTcall(C2H5OH_URL)
messenger.build_and_send_msg(C2H5OH, 'concentration_ppm', 'c2h5oh')

C3H8_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C3H8?access_token=da61a02b1808e7c4bd2965b75d4ca863'
C3H8 = messenger.wioRESTcall(C3H8_URL)
messenger.build_and_send_msg(C3H8, 'concentration_ppm', 'c3h8')

C4H10_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C4H10?access_token=da61a02b1808e7c4bd2965b75d4ca863'
C4H10 = messenger.wioRESTcall(C4H10_URL)
messenger.build_and_send_msg(C4H10, 'concentration_ppm', 'c4h10')

CH4_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/CH4?access_token=da61a02b1808e7c4bd2965b75d4ca863'
CH4 = messenger.wioRESTcall(CH4_URL)
messenger.build_and_send_msg(CH4, 'concentration_ppm', 'ch4')

CO_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/CO?access_token=da61a02b1808e7c4bd2965b75d4ca863'
CO = messenger.wioRESTcall(CO_URL)
messenger.build_and_send_msg(CO, 'concentration_ppm', 'co')

H2_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/H2?access_token=da61a02b1808e7c4bd2965b75d4ca863'
H2 = messenger.wioRESTcall(H2_URL)
messenger.build_and_send_msg(H2, 'concentration_ppm', 'h2')

NH3_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/NH3?access_token=da61a02b1808e7c4bd2965b75d4ca863'
NH3 = messenger.wioRESTcall(NH3_URL)
messenger.build_and_send_msg(NH3, 'concentration_ppm', 'nh3')

NO2_URL = 'https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/NO2?access_token=da61a02b1808e7c4bd2965b75d4ca863'
NO2 = messenger.wioRESTcall(NO2_URL)
messenger.build_and_send_msg(NO2, 'concentration_ppm', 'no2')

CO2_URL = 'https://us.wio.seeed.io/v1/node/GroveCo2MhZ16UART0/concentration?access_token=6b6b1b39ebd90be742a1f2d285788c01'
CO2 = messenger.wioRESTcall(CO2_URL)
messenger.build_and_send_msg(CO2, 'concentration', 'co2')

tempSHT31_URL = 'https://us.wio.seeed.io/v1/node/GroveTempHumiSHT31I2C0/temperature?access_token=dfe10a6d6f3f50a444dac66ca881436d'
tempSHT31 = messenger.wioRESTcall(tempSHT31_URL)
tempSHT31 = messenger.convertTemperature(tempSHT31, 'temperature')
if tempSHT31 != 8888 and tempSHT31 != 9999:
	messenger.build_and_send_msg(tempSHT31, 'temperature', 'extraTemp2')
else:
	print("TempSHT31 read error", tempSHT31);

humiditySHT31_URL = 'https://us.wio.seeed.io/v1/node/GroveTempHumiSHT31I2C0/humidity?access_token=dfe10a6d6f3f50a444dac66ca881436d'
humiditySHT31 = messenger.wioRESTcall(humiditySHT31_URL)
messenger.build_and_send_msg(humiditySHT31, 'humidity', 'extraHumid2')

# Currnetly off until we can find out how to translate into correct units
#sound_URL = 'https://us.wio.seeed.io/v1/node/GroveSoundA0/sound_level?access_token=dfe10a6d6f3f50a444dac66ca881436d'
#soundVal = messenger.wioRESTcall(sound_URL)
#messenger.build_and_send_msg(soundVal, 'sound_level', 'noise')
