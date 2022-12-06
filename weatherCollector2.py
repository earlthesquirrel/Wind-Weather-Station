import paho.mqtt.client as mqttClient
import time
import json

from mqttREST import mqttREST


messenger = mqttREST("gather-1", "weather-gather", "kfbqsegQF+8qqb6)ZH}o", 1883)

print
print("----------------------")

# Here's where we poll and gather data.

#altitudeBME_URL = 'https://172.16.0.7/v1/node/GroveBME280I2C1/altitude?access_token=5a2edc9d722be8466b4a88b6c037afbc'
altitudeBME_URL = 'https://172.16.0.12/v1/node/GroveBaroBMP280I2C1/altitude?access_token=7da8702ff1e9d84750fb3b29f3caa338'
altitudeBME = messenger.wioRESTcall(altitudeBME_URL)
altitudeBME = messenger.convertMetersToFeet(altitudeBME, 'altitude')
print("altitude BME", altitudeBME)
messenger.build_and_send_msg(altitudeBME, 'altitude', 'altimeter')


#tempBME_URL = 'https://172.16.0.7/v1/node/GroveBME280I2C1/temperature?access_token=5a2edc9d722be8466b4a88b6c037afbc'
tempBME_URL = 'https://172.16.0.12/v1/node/GroveBaroBMP280I2C1/temperature?access_token=7da8702ff1e9d84750fb3b29f3caa338'
tempBME = messenger.wioRESTcall(tempBME_URL)
tempB = messenger.getValue(tempBME, 'temperature')
tempBME = messenger.convertTemperature(tempBME, 'temperature')
print("tempBME", tempBME)
if tempBME != 8888 and tempBME != 9999:
     	messenger.build_and_send_msg(tempBME, 'temperature', 'extraTemp1')
else:
	print("TempBME read error", tempBME)


#humidityBME_URL = 'https://172.16.0.7/v1/node/GroveBME280I2C1/humidity?access_token=5a2edc9d722be8466b4a88b6c037afbc'
humidityBME_URL = 'https://172.16.0.12/v1/node/GroveBaroBMP280I2C1/humidity?access_token=7da8702ff1e9d84750fb3b29f3caa338'
humidityBME = messenger.wioRESTcall(humidityBME_URL)
print("humidityBME", humidityBME)
messenger.build_and_send_msg(humidityBME, 'humidity', 'extraHumid1')


#pressureBME_URL = 'https://172.16.0.7/v1/node/GroveBME280I2C1/pressure?access_token=5a2edc9d722be8466b4a88b6c037afbc'
pressureBME_URL = 'https://172.16.0.12/v1/node/GroveBaroBMP280I2C1/pressure?access_token=7da8702ff1e9d84750fb3b29f3caa338'
pressureBME = messenger.wioRESTcall(pressureBME_URL)
pressureB = messenger.getValue(pressureBME, 'pressure')
pressureBME = messenger.convertPressure(pressureBME, 'pressure')
print("pressure BME", pressureBME)


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



#tempCO2_URL = 'https://172.16.0.7/v1/node/GroveCo2MhZ16UART0/temperature?access_token=5a2edc9d722be8466b4a88b6c037afbc'
tempCO2_URL = 'https://172.16.0.12/v1/node/GroveCo2MhZ16UART0/temperature?access_token=7da8702ff1e9d84750fb3b29f3caa338'
tempCO2 = messenger.wioRESTcall(tempCO2_URL)
tempCO2 = messenger.convertTemperature(tempCO2, 'temperature')
print("tempCO2", tempCO2)
if tempCO2 != 8888 and tempCO2 != 9999:
	 messenger.build_and_send_msg(tempCO2, 'temperature', 'extraTemp3')
else:
	print("TempCO2 read error", tempCO2)


#humiditySHT35_URL = 'https://172.16.0.7/v1/node/GroveTempHumiSHT35I2C1/humidity?access_token=c5efbde3261ab282a444f6b79ae1085e'
humiditySHT35_URL = 'https://172.16.0.12/v1/node/GroveTempHumiSHT35I2C1/humidity?access_token=43c8af5564003ee7af29f3abee96983d'
humiditySHT35 = messenger.wioRESTcall(humiditySHT35_URL)
print("humiditySHT35", humiditySHT35)
messenger.build_and_send_msg(humiditySHT35, 'humidity', 'outHumidity')


#tempSHT35_URL = 'https://172.16.0.7/v1/node/GroveTempHumiSHT35I2C1/temperature?access_token=c5efbde3261ab282a444f6b79ae1085e'
tempSHT35_URL = 'https://172.16.0.12/v1/node/GroveTempHumiSHT35I2C1/temperature?access_token=43c8af5564003ee7af29f3abee96983d'
tempSHT35 = messenger.wioRESTcall(tempSHT35_URL)
tempSHT35 = messenger.convertTemperature(tempSHT35, 'temperature')
print("tempSHT35", tempSHT35)
if tempSHT35 != 8888 and tempSHT35 != 9999:
	messenger.build_and_send_msg(tempSHT35, 'temperature', 'outTemp')
else:
	print("TempSHT35 read error", tempSHT35)


#dust_URL = 'https://172.16.0.7/v1/node/GroveDustD1/dust?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
dust_URL = 'https://172.16.0.12/v1/node/GroveDustD0/dust?access_token=fc8ac11ff57cc7369fc2b9869e928ea5'
dust = messenger.wioRESTcall(dust_URL)
print("dust", dust)
messenger.build_and_send_msg(dust, 'dust', 'pm1_0')


#C2H5OH_URL = 'https://172.16.0.7/v1/node/GroveMultiChannelGasI2C0/C2H5OH?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
C2H5OH_URL = 'https://172.16.0.12/v1/node/GroveMultiChannelGasI2C1/C2H5OH?access_token=fc8ac11ff57cc7369fc2b9869e928ea5'
C2H5OH = messenger.wioRESTcall(C2H5OH_URL)
print("c2h5oh", C2H5OH)
messenger.build_and_send_msg(C2H5OH, 'concentration_ppm', 'c2h5oh')


#C3H8_URL = 'https://172.16.0.7/v1/node/GroveMultiChannelGasI2C0/C3H8?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
C3H8_URL = 'https://172.16.0.12/v1/node/GroveMultiChannelGasI2C1/C3H8?access_token=fc8ac11ff57cc7369fc2b9869e928ea5' 
C3H8 = messenger.wioRESTcall(C3H8_URL) 
print("c3h8", C3H8) 
messenger.build_and_send_msg(C3H8, 'concentration_ppm', 'c3h8')


#C4H10_URL = 'https://172.16.0.7/v1/node/GroveMultiChannelGasI2C0/C4H10?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
C4H10_URL = 'https://172.16.0.12/v1/node/GroveMultiChannelGasI2C1/C4H10?access_token=fc8ac11ff57cc7369fc2b9869e928ea5'
C4H10 = messenger.wioRESTcall(C4H10_URL)
print("c4h10", C4H10)
messenger.build_and_send_msg(C4H10, 'concentration_ppm', 'c4h10')


#CH4_URL = 'https://172.16.0.7/v1/node/GroveMultiChannelGasI2C0/CH4?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
CH4_URL = 'https://172.16.0.12/v1/node/GroveMultiChannelGasI2C1/CH4?access_token=fc8ac11ff57cc7369fc2b9869e928ea5'
CH4 = messenger.wioRESTcall(CH4_URL)
print("ch4", CH4)
messenger.build_and_send_msg(CH4, 'concentration_ppm', 'ch4')


#CO_URL = 'https://172.16.0.7/v1/node/GroveMultiChannelGasI2C0/CO?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
CO_URL = 'https://172.16.0.12/v1/node/GroveMultiChannelGasI2C1/CO?access_token=fc8ac11ff57cc7369fc2b9869e928ea5'
CO = messenger.wioRESTcall(CO_URL)
print("co", CO)
messenger.build_and_send_msg(CO, 'concentration_ppm', 'co')


#H2_URL = 'https://172.16.0.7/v1/node/GroveMultiChannelGasI2C0/H2?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
H2_URL = 'https://172.16.0.12/v1/node/GroveMultiChannelGasI2C1/H2?access_token=fc8ac11ff57cc7369fc2b9869e928ea5'
H2 = messenger.wioRESTcall(H2_URL)
print("h2", H2)
messenger.build_and_send_msg(H2, 'concentration_ppm', 'h2')


#NH3_URL = 'https://172.16.0.7/v1/node/GroveMultiChannelGasI2C0/NH3?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
NH3_URL = 'https://172.16.0.12/v1/node/GroveMultiChannelGasI2C1/NH3?access_token=fc8ac11ff57cc7369fc2b9869e928ea5'
NH3 = messenger.wioRESTcall(NH3_URL)
print("nh3", NH3)
messenger.build_and_send_msg(NH3, 'concentration_ppm', 'nh3')


#NO2_URL = 'https://172.16.0.7/v1/node/GroveMultiChannelGasI2C0/NO2?access_token=d5af96cc3a68f8030be5edd5f0da52d6'
NO2_URL = 'https://172.16.0.12/v1/node/GroveMultiChannelGasI2C1/NO2?access_token=fc8ac11ff57cc7369fc2b9869e928ea5'
NO2 = messenger.wioRESTcall(NO2_URL)
print("no2", NO2)
messenger.build_and_send_msg(NO2, 'concentration_ppm', 'no2')


#CO2_URL = 'https://172.16.0.7/v1/node/GroveCo2MhZ16UART0/concentration?access_token=5a2edc9d722be8466b4a88b6c037afbc'
CO2_URL = 'https://172.16.0.12/v1/node/GroveCo2MhZ16UART0/concentration?access_token=7da8702ff1e9d84750fb3b29f3caa338'
CO2 = messenger.wioRESTcall(CO2_URL)
print("co2", CO2)
messenger.build_and_send_msg(CO2, 'concentration', 'co2')


#tempSHT31_URL = 'https://172.16.0.7/v1/node/GroveTempHumiSHT31I2C0/temperature?access_token=98d89fd34a2946d169e0ad52c5f91b60'
tempSHT31_URL = 'https://172.16.0.12/v1/node/GroveTempHumiSHT31I2C0/temperature?access_token=9eb4a6891260d65b735e45c31fbe9739'
tempSHT31 = messenger.wioRESTcall(tempSHT31_URL)
tempSHT31 = messenger.convertTemperature(tempSHT31, 'temperature')
print("tempSHT31", tempSHT31)
if tempSHT31 != 8888 and tempSHT31 != 9999:
	messenger.build_and_send_msg(tempSHT31, 'temperature', 'extraTemp2')
else:
	print("TempSHT31 read error", tempSHT31);


#humiditySHT31_URL = 'https://172.16.0.7/v1/node/GroveTempHumiSHT31I2C0/humidity?access_token=98d89fd34a2946d169e0ad52c5f91b60'
humiditySHT31_URL = 'https://172.16.0.12/v1/node/GroveTempHumiSHT31I2C0/humidity?access_token=9eb4a6891260d65b735e45c31fbe9739'
humiditySHT31 = messenger.wioRESTcall(humiditySHT31_URL)
print("humiditySHT31", humiditySHT31)
messenger.build_and_send_msg(humiditySHT31, 'humidity', 'extraHumid2')



# Currnetly off until we can find out how to translate into correct units
#sound_URL = 'https://172.16.0.7/v1/node/GroveSoundA0/sound_level?access_token=98d89fd34a2946d169e0ad52c5f91b60'
sound_URL = 'https://172.16.0.12/v1/node/GroveSoundA0/sound_level?access_token=9eb4a6891260d65b735e45c31fbe9739'

#soundVal = messenger.wioRESTcall(sound_URL)
#messenger.build_and_send_msg(soundVal, 'sound_level', 'noise')
