import json, logging, sys, socket
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


logger = logging.getLogger("TSmart_Write")

TSMode=["Manual","Eco","Smart","Timer", "Travel", "Boost"]
TSSmartState=["Uninitialised","Idle","Recording","Reproduction"]

def checksum(input):
    input.append(85)
    bufferPayload=bytes(input)
    chksum = 0
    for byte in bufferPayload:
        chksum ^= byte
    input.pop()
    input.append(chksum)
    output=bytes(input)
    return output

def sendCommand(bytesToSend):
    serverAddressPort= (TSmartSettings.IP_Address, 1337)
    bufferSize= 1028
    logging.info("Sending Control Write message")
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)


def setMode(payload):
    temp={}
    targetresult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        #get int from posiiton in LUT
        modeInt=int(list(TSMode).index(payload['mode']))
        bufferpayload=checksum([242,0,0,1,0,0,modeInt])
        sendCommand(bufferpayload)
    except:
        e = sys.exc_info()
        temp['result']="Setting Mode failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)

def setSetPoint(payload):
    temp={}
    targetresult="Success"
    tempint2=0
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        tempInt=int(float(payload['temperature'])*10)
        #pad and make little Endian
        LE=tempInt.to_bytes(2, byteorder="little")
        temps=list(LE)
        bufferpayload=checksum([242,0,0,1,temps[0],temps[1],0])
        sendCommand(bufferpayload)
    except:
        e = sys.exc_info()
        temp['result']="Setting Mode failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)

def setPower(payload):
    temp={}
    targetresult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        #get int from posiiton in LUT
        powerInt=int(payload['power'])
        bufferpayload=checksum([242,0,0,powerInt,0,0,0])
        sendCommand(bufferpayload)
    except:
        e = sys.exc_info()
        temp['result']="Setting Mode failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)