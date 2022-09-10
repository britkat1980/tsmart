import subprocess, sys, os, logging
import read
from time import sleep
import pathlib
path = os.getcwd()
os.chdir(os.getcwd()+"/TSmart")
logging.critical("CWD: "+os.getcwd())
#sys.path.append(str(THISPATH)+"\\TSmart")
from settings import TSmartSettings

logging.critical("Starting the Server...")
serverpid=subprocess.Popen(["python3","server.py"])

logging.critical("Starting Control Read loop")

while True:
    read.controlRead()
    sleep (TSmartSettings.self_run_timer)