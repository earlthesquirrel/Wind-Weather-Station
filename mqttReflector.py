import paho.mqtt.client as mqttClient
import time
import json

### weather/radiation
def on_message_radiation(mosq, obj, msg):
	#print("In Radiation Callback")
    	mosq.publish("weather", msg.payload);
	print("Message is: "+msg.payload)

## /ea14e76e308ff50a0e09a7e5bf96749a/air/heatindex
def on_message_heatindex(mosq, obj, msg):

	#print("In HeadIndexCallback")
	j = json.loads(msg.payload)
	value = j["heatindex"]; 
       	epoch_time = int (time.time())
       	message = '{"dateTime":'+str(epoch_time)+', "inHeatIndex" : '+str(value)+'}'
    	mosq.publish("weather", message);
	print("Message is :"+message);
	return

## /ea14e76e308ff50a0e09a7e5bf96749a/air/temperature
def on_message_temperature(mosq, obj, msg):

	#print("In TempCallback")
	j = json.loads(msg.payload)
	value = j["temperature"]; 
        epoch_time = int (time.time())
        message = '{"dateTime":'+str(epoch_time)+', "inTemp" : '+str(value)+'}'
    	mosq.publish("weather", message);
	print("Message is :"+message);
	return

## /ea14e76e308ff50a0e09a7e5bf96749a/air/humidity
def on_message_humidity(mosq, obj, msg):

	#print("In HumidityCallback")
	j = json.loads(msg.payload)
	value = j["humidity"];
       	epoch_time = int (time.time())
       	message = '{"dateTime":'+str(epoch_time)+', "inHumidity" : '+str(value)+'}'
   	mosq.publish("weather", message);
	print("Message is :"+message);
	return

### topic message
def on_message(mosq, obj, msg):
    	print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
	return

global Connected                #Use global variable

def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
        print("Connected to broker")
        Connected = True                #Signal connection 

	# Resubscribe...
	mqtt_topics = ["/weather/raditation", "/ea14e76e308ff50a0e09a7e5bf96749a/air/temperature", "/ea14e76e308ff50a0e09a7e5bf96749a/air/humidity", "/ea14e76e308ff50a0e09a7e5bf96749a/air/heatindex"]
	for topic in mqtt_topics:
        	mqttc.subscribe(topic)
    else:
        print("Connection failed")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection." + str(rc));
	print(str( time.time() ) ) ;


def on_publish(client,userdata,mid):             #create function for callback
    print("data published")
    print(mid)


### topic message
def on_message(mosq, obj, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))


def on_log(client, userdata, level, buf):
    print("log: ",buf)


mqttc = mqttClient.Client("r1-python")               			# create new instance
mqttc.username_pw_set("mqtt-reflector", "CVE6}oG9d,nY,hQGGPhj")   	# set username and password

mqttc.on_connect= on_connect              		# attach connection function callback
mqttc.on_disconnect= on_disconnect              	# attach disconnect function callback

mqttc.connect("172.16.0.4", 1883, 120)


# Add message callbacks that will only trigger on a specific subscription match

mqttc.message_callback_add('/weather/raditation', on_message_radiation)
mqttc.message_callback_add('/ea14e76e308ff50a0e09a7e5bf96749a/air/temperature', on_message_temperature)
mqttc.message_callback_add('/ea14e76e308ff50a0e09a7e5bf96749a/air/humidity', on_message_humidity)
#mqttc.message_callback_add('/ea14e76e308ff50a0e09a7e5bf96749a/air/heatindex', on_message_heatindex)

#mqttc.on_message = on_message	# General Message receiver, useful for debugging
#mqttc.on_publish = on_publish	
#mqttc.on_log = on_log

mqttc.loop_forever(90, 1, False);

# Data that could be added.
# Client mosqsub|12755-mqttpi received PUBLISH (d0, q0, r0, m0, '/weather/raditation', ... (66 bytes))
# { "dateTime" : 1603913320, "cps" :  0, "cpm" : 16, "usvhr" : 0.09}
# Client mosqsub|12755-mqttpi received PUBLISH (d0, q0, r0, m0, '/ea14e76e308ff50a0e09a7e5bf96749a/BMPpressure', ... (22 bytes))
# {"BMPpressure":978.22}
# Client mosqsub|12755-mqttpi received PUBLISH (d0, q0, r0, m0, 'ea14e76e308ff50a0e09a7e5bf96749a/BMPtemperature', ... (24 bytes))
# {"BMPtemperature":80.78}
# Client mosqsub|12755-mqttpi received PUBLISH (d0, q0, r0, m0, '/ea14e76e308ff50a0e09a7e5bf96749a/air/temperature', ... (22 bytes))
# {"temperature":77.684}
# Client mosqsub|12755-mqttpi received PUBLISH (d0, q0, r0, m0, '/ea14e76e308ff50a0e09a7e5bf96749a/air/humidity', ... (17 bytes))
# {"humidity":48.5}
# Client mosqsub|12755-mqttpi received PUBLISH (d0, q0, r0, m0, '/ea14e76e308ff50a0e09a7e5bf96749a/air/heatindex', ... (22 bytes))
# {"heatindex":77.43144}
#Client mosqsub|21190-mqttpi received PUBLISH (d0, q0, r0, m0, '/c3019c69cac288d287f0de1ecf45f37c/AirQuality', ... (18 bytes))
#{"Quality":"Poor"}
#Client mosqsub|21190-mqttpi received PUBLISH (d0, q0, r0, m0, '/c3019c69cac288d287f0de1ecf45f37c/DangerousGas', ... (2 bytes))
#ON
#Client mosqsub|21190-mqttpi received PUBLISH (d0, q0, r0, m0, '/c3019c69cac288d287f0de1ecf45f37c/AirConductivity', ... (19 bytes))
#{"Conductivity":46}
