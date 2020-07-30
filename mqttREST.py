import requests
import paho.mqtt.client as mqttClient
import time
import json

class mqttREST:

    _user      = None
    _password  = None
    _port      = None
    _client    = None

    def __init__( self, user, password, port ):

        self._user = user
        self._password = password
        self._port = port


    def wioRESTcall(self, url):

       r = requests.get(url)

       #print(r.status_code)
       #print(r.json())

       # return (str.replace(str(r.json()),"u'","'"))

       if  r.status_code == 200 :
          return r.json()
       else:
          return "ERROR" 


    def on_connect(self, client, userdata, flags, rc):
 
        if rc == 0:
            print("Connected to broker")
     
            global Connected                #Use global variable
            Connected = True                #Signal connection 
 
        else:
            print("Connection failed")
 

    def build_msg(self, measurement):

        epoch_time = int (time.time())
        message = '{"dateTime":'+str(epoch_time)+','+measurement+'}'
    
        return message


    def send_msg(self, value):

        broker_address= "172.16.0.4"

	try:   
            self._client = mqttClient.Client("Python")               # create new instance
            self._client.username_pw_set(self._user, self._password)    # set username and password
            self._client.on_connect= self.on_connect                 # attach function to callback
            self._client.connect(broker_address, self._port)          # connect to broker
            self._client.publish("weather",value)
            self._client.disconnect()
	except socket.timeout
	    print "Got socket timeout, continuing..."
	    print "Data was " + value;



    def build_and_send_msg(self, data, key, label):

        if  data != 'ERROR':
	    if data:
	       value = data[key]
       	       if value is not None:
                  msg = self.build_msg('"'+label+'":'+str(value))
                  self.send_msg(msg)
	       else:
		    print('In build and send msg {} caused issue on key {}'.format(data, key));
	    else:
	        print('In build and send msg {} caused issue'.format(data));
       
    def convertPressure( self, data, key ):
        if data != 'ERROR' :
	    value = data[key]
            if value is not None:
               calc = data[key] * 0.00029529983071445
               data[key] = calc
            else:
	       print('In convertPressure {} caused issue on key {}'.format(data, key));
            return data
    
    def convertTemperature( self, data, key ):
        if data != 'ERROR' :
	    value = data[key]
            if value is not None:
                calc = ( value * 9/5) + 32
                data[key] = calc
	    else:
	        print('In convertTemp {} caused issue on key {}'.format(data, key));
            return data

    def convertMetersToFeet( self, data, key ):
        if data != 'ERROR' :
	    value = data[key]
            if value is not None:
                calc = value * 3.2808
                data[key] = calc
	    else:
	        print('In converMetersToFeet {} caused issue on key {}'.format(data, key));
            return data
 
