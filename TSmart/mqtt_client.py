import paho.mqtt.client as mqtt
import time
import sys
import importlib
import logging
from logging.handlers import TimedRotatingFileHandler
from settings import TSmartSettings
import write as wr

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


logger = logging.getLogger("TSmart_MQTT_client_")

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
if TSmartSettings.MQTT_Topic=='':
    MQTT_Topic='GivEnergy'
else:
    MQTT_Topic=TSmartSettings.MQTT_Topic
    
def on_message(client, userdata, message):
    logger.info("MQTT Message Recieved: "+str(message.topic)+"= "+str(message.payload.decode("utf-8")))
    writecommand={}
    command=str(message.topic).split("/")[-1]
    if command=="setMode":
        logger.critical("Setting TSmart Mode to: "+str(message.payload.decode("utf-8")))
        writecommand['mode']=str(message.payload.decode("utf-8"))
        result=wr.setMode(writecommand)
    elif command=="setSetPoint":
        logger.critical("Setting Target Temp to: "+str(message.payload.decode("utf-8")))
        writecommand['temperature']=str(message.payload.decode("utf-8"))
        result=wr.setSetPoint(writecommand)
    elif command=="setPower":
        logger.critical("Setting Power Mode to: "+str(message.payload.decode("utf-8")))
        writecommand['power']=str(message.payload.decode("utf-8"))
        result=wr.setPower(writecommand)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        logger.info("connected OK Returned code="+str(rc))
        #Subscribe to the control topic for this invertor - relies on serial_number being present
        client.subscribe(MQTT_Topic+"/Control/#")
        logger.info("Subscribing to "+MQTT_Topic+"/Control/#")
    else:
        logger.error("Bad connection Returned code= "+str(rc))


client=mqtt.Client("TSmart_MQTT_Client")
mqtt.Client.connected_flag=False        			#create flag in class
if MQTTCredentials:
    client.username_pw_set(MQTT_Username,MQTT_Password)
client.on_connect=on_connect     			        #bind call back function
client.on_message=on_message                        #bind call back function
#client.loop_start()

logger.info ("Connecting to broker(sub): "+ MQTT_Address)
client.connect(MQTT_Address,port=MQTT_Port)
client.loop_forever()