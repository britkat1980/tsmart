# tsmart

Docker container which connects via UDP to a T-Smart water heater thermostat and integrates into Home Assistant via MQTT.

## Installation

### Docker

Use the [docker-compose.yaml](docker-compose.yaml) file and modify to suit your scenario. Start with:

`docker-compose up -d`

TSmart entities should be added to Home Assistant automatically if you have MQTT setup.

### Home Assistant

Navigate to Settings->Addons->Addon Store

* Click the triple dots top right and “Repositories”
* Add: “https://github.com/britkat1980/tsmart”
* It will add TSmart as an addon for you to install
* Install it then open the config tab and add the following info:
    * IP address of your TSmart
    * IP Address of the HA MQTT broker
    * add MQTT username and password if you use them
* Save config and then start the addon
* The Addon will create a Climate device which will allow you to set the mode (using “presets”) and the temp using the usual climate controls.
