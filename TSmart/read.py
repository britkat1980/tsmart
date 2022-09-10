import logging, socket, sys
from settings import TSmartSettings
from time import sleep

def controlRead():
    msgFromClient= [241,0,0,164]
    bytesToSend = bytearray(msgFromClient)
    serverAddressPort= (TSmartSettings.IP_Address, 1337)
    bufferSize= 1028
    logging.info("Sending Control Read message")
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

def self_run():
    while True:
        controlRead()
        sleep (TSmartSettings.self_run_timer)

if __name__ == '__main__':
    if len(sys.argv)==2:
        globals()[sys.argv[1]]()
    elif len(sys.argv)==3:
        globals()[sys.argv[1]](sys.argv[2])