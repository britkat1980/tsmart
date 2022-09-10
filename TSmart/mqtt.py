# version 2022.01.21
import paho.mqtt.client as mqtt
import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from settings import TSmartSettings

if TSmartSettings.Log_Level.lower()=="debug":
    if TSmartSettings.Debug_File_Location=="":
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(),TimedRotatingFileHandler(TSmartSettings.Debug_File_Location, when='D', interval=1, backupCount=7)])
elif TSmartSettings.Log_Level.lower()=="info":
    if TSmartSettings.Debug_File_Location=="":
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(),TimedRotatingFileHandler(TSmartSettings.Debug_File_Location, when='D', interval=1, backupCount=7)])
else:
    if TSmartSettings.Debug_File_Location=="":
        logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(),TimedRotatingFileHandler(TSmartSettings.Debug_File_Location, when='D', interval=1, backupCount=7)])


logger = logging.getLogger("TSmart_MQTT")

class TSmartMQTT():

    if TSmartSettings.MQTT_Port=='':
        MQTT_Port=1883
    else:
        MQTT_Port=int(TSmartSettings.MQTT_Port)
    MQTT_Address=TSmartSettings.MQTT_Address
    if TSmartSettings.MQTT_Username=='':
        MQTTCredentials=False
    else:
        MQTTCredentials=True
        MQTT_Username=TSmartSettings.MQTT_Username
        MQTT_Password=TSmartSettings.MQTT_Password

    def on_connect(client, userdata, flags, rc):
        if rc==0:
            client.connected_flag=True #set flag
            logger.info("connected OK Returned code="+str(rc))
            #client.subscribe(topic)
        else:
            logger.info("Bad connection Returned code= "+str(rc))
    
    def multi_MQTT_publish(rootTopic,array):   #Recieve multiple payloads with Topics and publish in a single MQTT connection
        mqtt.Client.connected_flag=False        			#create flag in class
        client=mqtt.Client("TSmart_MQTT")
        
        ##Check if first run then publish auto discovery message
        
        if TSmartMQTT.MQTTCredentials:
            client.username_pw_set(TSmartMQTT.MQTT_Username,TSmartMQTT.MQTT_Password)
        client.on_connect=TSmartMQTT.on_connect     			#bind call back function
        client.loop_start()
        logger.info ("Connecting to broker: "+ TSmartMQTT.MQTT_Address)
        client.connect(TSmartMQTT.MQTT_Address,port=TSmartMQTT.MQTT_Port)
        while not client.connected_flag:        			#wait in loop
            logger.info ("In wait loop")
            time.sleep(0.2)
        for p_load in array:
            payload=array[p_load]
            logger.info('Publishing: '+rootTopic+p_load)
            output=TSmartMQTT.iterate_dict(payload,rootTopic+p_load)   #create LUT for MQTT publishing
            for value in output:
                client.publish(value,output[value])
        client.loop_stop()                      			#Stop loop
        client.disconnect()
        return client

    def iterate_dict(array,topic):      #Create LUT of topics and datapoints
        MQTT_LUT={}
        if isinstance(array, dict):
            # Create a publish safe version of the output
            for p_load in array:
                output=array[p_load]
                if isinstance(output, dict):
                    MQTT_LUT.update(TSmartMQTT.iterate_dict(output,topic+"/"+p_load))
                    logger.info('Prepping '+p_load+" for publishing")
                else:
                    MQTT_LUT[topic+"/"+p_load]=output
        else:
            MQTT_LUT[topic]=array
        return(MQTT_LUT)