# version 2022.01.21
from array import array
import logging
from logging.handlers import TimedRotatingFileHandler
import paho.mqtt.client as mqtt
import time
import datetime
import json

import logging  
from settings import TSmartSettings
from mqtt import TSmartMQTT

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


logger = logging.getLogger("TSmart_HA_AUTO")

class HAMQTT():

    entity_type={
        #"Battery_Discharge_Rate":["number","","setDischargeRate"],
        "Power":["switch","","setPower"],
        "Set_Point":["sensor","temperature"],
        "Mode":["select","","setMode"],
        "High_Temperature":["sensor","temperature"],
        "Low_Temperature":["sensor","temperature"],
        "Heating":["binary_sensor",""],
        "Smart_State":["select","","setSmartState"],
        "Thermostat":["climate",""],
        "Auto":["",""],
        "Power_W":["sensor","power"]
        }

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
    if TSmartSettings.MQTT_Topic=="":
        TSmartSettings.MQTT_Topic="TSmart"


    def on_connect(client, userdata, flags, rc):
        if rc==0:
            client.connected_flag=True #set flag
            logger.info("connected OK Returned code="+str(rc))
            #client.subscribe(topic)
        else:
            logger.info("Bad connection Returned code= "+str(rc))
    
    def publish_discovery(array):   #Recieve multiple payloads with Topics and publish in a single MQTT connection
        mqtt.Client.connected_flag=False        			#create flag in class
        client=mqtt.Client("TSmart")
        rootTopic=str(TSmartSettings.MQTT_Topic+"/")
        if HAMQTT.MQTTCredentials:
            client.username_pw_set(HAMQTT.MQTT_Username,HAMQTT.MQTT_Password)
        client.on_connect=HAMQTT.on_connect     			#bind call back function
        client.loop_start()
        logger.info ("Connecting to broker: "+ HAMQTT.MQTT_Address)
        client.connect(HAMQTT.MQTT_Address,port=HAMQTT.MQTT_Port)
        while not client.connected_flag:        			#wait in loop
            logger.info ("In wait loop")
            time.sleep(0.2)
            ##publish the status message
            client.publish(TSmartSettings.MQTT_Topic+"/status","online", retain=True)
        ### For each topic create a discovery message
            for p_load in array:
                if p_load != "raw":
                    payload=array[p_load]
                    logger.info('Publishing: '+rootTopic+p_load)
                    output=TSmartMQTT.iterate_dict(payload,rootTopic+p_load)   #create LUT for MQTT publishing
                    for topic in output:
                        #Determine Entitiy type (switch/sensor/number) and publish the right message
                        if HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="sensor":
                            if "Battery_Details" in topic:
                                client.publish("homeassistant/sensor/TSmart/"+str(topic).split("/")[-2]+"_"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic),retain=True)
                            else:
                                client.publish("homeassistant/sensor/TSmart/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic),retain=True)
                        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="switch":
                            client.publish("homeassistant/switch/TSmart/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic),retain=True)
                        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="number":
                            client.publish("homeassistant/number/TSmart/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic),retain=True)
                        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="binary_sensor":
                            client.publish("homeassistant/binary_sensor/TSmart/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic),retain=True)
                        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="select":
                            client.publish("homeassistant/select/TSmart/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic),retain=True)
                        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="climate":
                            client.publish("homeassistant/climate/TSmart/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic),retain=True)
                            
                           
        client.loop_stop()                      			#Stop loop
        client.disconnect()
        return client

    def create_device_payload(topic):
        tempObj={}
        tempObj['stat_t']=str(topic).replace(" ","_")
        tempObj['avty_t'] = TSmartSettings.MQTT_Topic+"/status"
        tempObj["pl_avail"]= "online"
        tempObj["pl_not_avail"]= "offline"
        tempObj['device']={}
        
        TSmart_Device=str(topic).split("/")[1]
        tempObj['uniq_id']=TSmart_Device+"_"+str(topic).split("/")[-1]
        tempObj['device']['identifiers']=TSmartSettings.ha_device_prefix
        tempObj['device']['name']=TSmartSettings.ha_device_prefix
        tempObj["name"]=TSmartSettings.ha_device_prefix+" "+str(topic).split("/")[-1].replace("_"," ") #Just final bit past the last "/"
        tempObj['device']['manufacturer']="TSmart"

        try:
            tempObj['command_topic']=TSmartSettings.MQTT_Topic+"/control/"+HAMQTT.entity_type[str(topic).split("/")[-1]][2]
        except:
            pass
#set device specific elements here:
        if HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="sensor":
            tempObj['unit_of_meas']=""
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="energy":
                tempObj['unit_of_meas']="kWh"
                tempObj['device_class']="Energy"
                if topic.split("/")[-2]=="Total":
                    tempObj['state_class']="total"
                else:
                    tempObj['state_class']="total_increasing"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="money":
                tempObj['unit_of_meas']="{GBP}/kWh"
                tempObj['device_class']="Monetary"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="power":
                tempObj['unit_of_meas']="W"
                tempObj['device_class']="Power"
                tempObj['state_class']="measurement"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="temperature":
                tempObj['unit_of_meas']="C"
                tempObj['device_class']="Temperature"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="voltage":
                tempObj['unit_of_meas']="V"
                tempObj['device_class']="Voltage"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="current":
                tempObj['unit_of_meas']="A"
                tempObj['device_class']="Current"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="battery":
                tempObj['unit_of_meas']="%"
                tempObj['device_class']="Battery"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="timestamp":
                del(tempObj['unit_of_meas'])
                tempObj['device_class']="timestamp"
        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="switch":
            tempObj['payload_on']="On"
            tempObj['payload_off']="Off"
        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="binary_sensor":
            tempObj['payload_on']="On"
            tempObj['payload_off']="Off"
        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="select":
            if TSmart_Device=="Mode":
                options=["Manual","Eco","Smart","Timer", "Travel", "Boost"]
                tempObj['options']=options
            if TSmart_Device=="Smart_State":
                options=["Uninitialised","Idle","Recording","Reproduction"]
                tempObj['options']=options
        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="number":
            tempObj['unit_of_meas']="%"
        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="climate":
            tempObj['current_temperature_topic']=TSmartSettings.MQTT_Topic+"/Low_Temperature"
            tempObj['temperature_state_topic']=TSmartSettings.MQTT_Topic+"/Set_Point"
            tempObj['min_temp']=10
            tempObj['max_temp']=70
            tempObj['preset_mode_command_topic']=TSmartSettings.MQTT_Topic+"/Control/setMode"
            tempObj['preset_mode_state_topic']=TSmartSettings.MQTT_Topic+"/Mode"
            tempObj['mode_state_topic']=TSmartSettings.MQTT_Topic+"/Auto"
            tempObj['mode_command_topic']=TSmartSettings.MQTT_Topic+"/Control/Auto"
            tempObj['power_command_topic']=TSmartSettings.MQTT_Topic+"/Control/setPower"
            tempObj['temperature_command_topic']=TSmartSettings.MQTT_Topic+"/Control/setSetPoint"
            tempObj['preset_modes']=["Manual","Eco","Smart","Timer", "Travel", "Boost"]
        ## Convert this object to json string
        jsonOut=json.dumps(tempObj)
        return(jsonOut)