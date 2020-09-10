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
pressureBME = messenger.convertPressure(pressureBME, 'pressure')
messenger.build_and_send_msg(pressureBME, 'pressure', 'barometer')

humiditySHT_URL = 'https://us.wio.seeed.io/v1/node/GroveTempHumiSHT31I2C0/humidity?access_token=d5c417d04b21aaa4683c0f99c711532a'
humiditySHT = messenger.wioRESTcall(humiditySHT_URL)
#messenger.build_and_send_msg(humiditySHT, 'humidity', 'extraHumid1')
messenger.build_and_send_msg(humiditySHT, 'humidity', 'outHumidity')

tempSHT_URL = 'https://us.wio.seeed.io/v1/node/GroveTempHumiSHT31I2C0/temperature?access_token=d5c417d04b21aaa4683c0f99c711532a'
tempSHT = messenger.wioRESTcall(tempSHT_URL)
tempSHT = messenger.convertTemperature(tempSHT, 'temperature')
if tempSHT != 8888 and tempSHT != 9999:
	# messenger.build_and_send_msg(tempSHT, 'temperature', 'extraTemp1')
	messenger.build_and_send_msg(tempSHT, 'temperature', 'outTemp')
else:
	print("TempSHT read error", tempSHT)

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

