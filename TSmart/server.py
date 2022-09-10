
from ipaddress import ip_address
import socket
import sys
import logging
from settings import TSmartSettings
import re
from mqtt import TSmartMQTT
import os
import datetime
from logging.handlers import TimedRotatingFileHandler

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

TSMode=["Manual","Eco","Smart","Timer", "Travel", "Boost"]
TSSmartState=["Uninitialised","Idle","Recording","Reproduction"]

logger = logging.getLogger("TSmart_HA_AUTO")

def to_little(val):
  little_hex = bytearray.fromhex(val)
  little_hex.reverse()
  logger.debug("Byte array format:", little_hex)

  str_little = ''.join(format(x, '02x') for x in little_hex)

  return str_little

def publishOutput(array):
    tempoutput={}
    tempoutput=iterate_dict(array)

    if TSmartSettings.MQTT_Output:
        if TSmartSettings.first_run:        # Home Assistant MQTT Discovery
            from HA_Discovery import HAMQTT
            HAMQTT.publish_discovery(tempoutput)
            TSmartSettings.first_run=False
            updateFirstRun()
        from mqtt import TSmartMQTT
        logger.info("Publish all to MQTT")
        if TSmartSettings.MQTT_Topic=="":
            TSmartSettings.MQTT_Topic="TSmart"
        TSmartMQTT.multi_MQTT_publish(str(TSmartSettings.MQTT_Topic+"/"), tempoutput)


def iterate_dict(array):        # Create a publish safe version of the output (convert non string or int datapoints)
    safeoutput={}
    for p_load in array:
        output=array[p_load]
        if isinstance(output, dict):
            temp=iterate_dict(output)
            safeoutput[p_load]=temp
            logger.info('Dealt with '+p_load)
        elif isinstance(output, tuple):
            if "slot" in str(p_load):
                logger.info('Converting Timeslots to publish safe string')
                safeoutput[p_load+"_start"]=output[0].strftime("%H:%M")
                safeoutput[p_load+"_end"]=output[1].strftime("%H:%M")
            else:
                #Deal with other tuples _ Print each value
                for index, key in enumerate(output):
                    logger.info('Converting Tuple to multiple publish safe strings')
                    safeoutput[p_load+"_"+str(index)]=str(key)
        elif isinstance(output, datetime.datetime):
            logger.info('Converting datetime to publish safe string')
            safeoutput[p_load]=output.strftime("%d-%m-%Y %H:%M:%S")
        elif isinstance(output, datetime.time):
            logger.info('Converting time to publish safe string')
            safeoutput[p_load]=output.strftime("%H:%M")
            safeoutput[p_load]=output.name
        elif isinstance(output, float):
            safeoutput[p_load]=round(output,2)
        else:
            safeoutput[p_load]=output
    return(safeoutput)

def updateFirstRun():
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "settings.py"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path, "r") as f:
        lines = f.readlines()
    with open(abs_file_path, "w") as f:
        for line in lines:
            if line.strip("\n") == "    first_run= True":
                f.write("    first_run= False\n")
            else:
                f.write(line)


logging.critical("Inside server.py")
localIP     = "0.0.0.0"
localPort   = 1337
bufferSize  = 1024
output={}
try:
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Bind to address and ip
    UDPServerSocket.bind((localIP, localPort))
    logging.critical("UDP server up and listening")
except:
    e = sys.exc_info()
    logging.error("Error: " + str(e))

    # Listen for incoming datagrams
while(True):

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    clientMsg = "Message from Client:{}".format(message)
    clientIP  = "Client IP Address:{}".format(address)
    logger.info(clientIP+": "+clientMsg)

    if address[0]==TSmartSettings.IP_Address:
        response=message.hex()
        if response[0:2]=="f1":
            messagetype="ControlRead"
            if response[6:8]=="01":
                output['Power']="On" 
            else: 
                output['Power']="Off"
            output['Set_Point']=int(to_little(response[8:12]),16)/10
            output['Mode']=TSMode[int(response[12:14],16)]
            output['High_Temperature']=int(to_little(response[14:18]),16)/10
            if response[18:20]=="01":
                output['Heating']="On"
                output['Power_W']=3000
            else: 
                output['Heating']="Off"
                output['Power_W']=0
            output['Smart_State']=TSSmartState[int(response[20:22],16)]
            output['Low_Temperature']=int(to_little(response[22:26]),16)/10
            logger.info("Data recieved")
            output['Auto']="auto"
            output['Thermostat']=""
            publishOutput(output)


