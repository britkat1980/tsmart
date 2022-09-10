from genericpath import exists
import os
import subprocess
from time import sleep
import logging
path = os.getcwd()
from time import sleep
import pathlib
path = os.getcwd()
os.chdir(os.getcwd()+"/TSmart")
logging.critical("CWD: "+os.getcwd())

logging.basicConfig(level=logging.CRITICAL, format="%(asctime)s %(name)s - %(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger("TSmart_STARTUP")

# Remove old settings file
if exists("settings.py"):
    os.remove("settings.py")
FILENAME=""
# create settings file
logger.critical ("Recreating settings.py")
with open("settings.py", 'w') as outp:
    outp.write("class TSmartSettings:\n")
    outp.write("    IP_Address=\""+str(os.getenv("IP_Address")+"\"\n"))
    outp.write("    MQTT_Output="+str(os.getenv("MQTT_Output")+"\n"))
    outp.write("    MQTT_Address=\""+str(os.getenv("MQTT_Address")+"\"\n"))
    outp.write("    MQTT_Username=\""+str(os.getenv("MQTT_Username")+"\"\n"))
    outp.write("    MQTT_Password=\""+str(os.getenv("MQTT_Password")+"\"\n"))
    outp.write("    MQTT_Topic=\""+str(os.getenv("MQTT_Topic")+"\"\n"))
    outp.write("    MQTT_Port="+str(os.getenv("MQTT_Port")+"\n"))
    outp.write("    Log_Level=\""+str(os.getenv("Log_Level")+"\"\n"))
    #setup debug filename for each inv
    if str(os.getenv("Debug_File_Location"))!="": FILENAME=str(os.getenv("Debug_File_Location"))
    outp.write("    Debug_File_Location=\""+str(FILENAME+"\"\n"))
    outp.write("    first_run= True\n")
    outp.write("    self_run_timer="+str(os.getenv("self_run_timer"))+"\n")
    outp.write("    ha_device_prefix=\""+str(os.getenv("ha_device_prefix"))+"\"\n")

# replicate the startup script here:
logging.critical("Starting the Server...")
serverpid=subprocess.Popen(["python3","server.py"])
logging.critical("Starting the MQTT CLient...")
mqttClientpid=subprocess.Popen(["python3","mqtt_client.py"])
logging.critical("Starting Control Read loop every: "+str(os.getenv("self_run_timer"))+"s")
readpid=subprocess.Popen(["python3","read.py","self_run"])

while (True):
    if not serverpid.poll()==None:
        logger.error("UDP Server died. restarting...")
        logger.critical ("Starting UDP Server")
        serverpid=subprocess.Popen(["python3","server.py"])
    if not mqttClientpid.poll()==None:
        logger.error("MQTT Client died. restarting...")
        logging.critical("Starting the MQTT Client...")
        mqttClientpid=subprocess.Popen(["python3","mqtt_client.py"])
    if not readpid.poll()==None:
        logger.error("Control read loop died. restarting...")
        logging.critical("Starting Control Read loop every: "+str(os.getenv("self_run_timer"))+"s")
        readpid=subprocess.Popen(["python3","read.py","self_run"])
    sleep(60)
    