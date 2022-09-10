# set base image (host OS)
FROM python:rc-alpine

RUN apk add curl
# Install nodejs for the dashboard
#RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

COPY TSmart TSmart
COPY startup.py .

ENV IP_Address="192.168.2.142"
ENV self_run_timer=10
ENV Log_Level="Error"
ENV Debug_File_Location=""
ENV Print_Raw_Registers=True
#MQTT Output Settings
ENV MQTT_Output=True
ENV MQTT_Address=""
ENV MQTT_Username=""
ENV MQTT_Password=""
ENV MQTT_Topic="TSmart"
ENV MQTT_Port=1883
ENV ha_device_prefix="TSmart"


EXPOSE 1337

CMD ["python3", "/app/startup.py"]
