#!/usr/bin/env python3
__author__ = "Diogo Gomes"
__version__ = "0.0.1"
__email__ = "diogogomes@gmail.com"

import argparse
import logging
import json

import serial
import paho.mqtt.client as mqtt

MQTT_BASE_TOPIC = "serial2mqtt"
MQTT_SERIAL2MQTT_STATUS = MQTT_BASE_TOPIC+"/status"
MQTT_AVAILABLE = "online"
MQTT_NOT_AVAILABLE = "offline"

HA_DISCOVERY_PREFIX="homeassistant/sensor/{}/config"

def gen_ha_config(mqtt_base_topic, name):
    json_config = {
        "name": name,
        "state_topic": "{}/{}".format(mqtt_base_topic, name), 
        "availability_topic": MQTT_SERIAL2MQTT_STATUS,
        "payload_available": MQTT_AVAILABLE,
        "payload_not_available": MQTT_NOT_AVAILABLE,
    }
    return json.dumps(json_config)

log_format = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, result):
    client.publish(MQTT_SERIAL2MQTT_STATUS,MQTT_AVAILABLE,retain=True)

def main_loop(sensor_name, port, speed, mqtt_server, mqtt_port, mqtt_base_topic):
    try:
        logger.info("Attaching to... %s @ %s", port, speed)
        ser = serial.Serial(port, speed, timeout=20)
        ser.flushInput()
    except Exception as e:
        logger.error("Failed to connect serial: %s", e)
        raise SystemExit


    logger.debug("Connecting to %s:%s", mqtt_server, mqtt_port)
    mqttc = mqtt.Client(client_id="serial2mqtt", userdata={'mqtt_base_topic': mqtt_base_topic, 'name': sensor_name})
    mqttc.will_set(MQTT_SERIAL2MQTT_STATUS,MQTT_NOT_AVAILABLE,retain=True)
    mqttc.on_connect = on_connect

    # Add message callbacks that will only trigger on a specific subscription match.
    mqttc.connect(mqtt_server, mqtt_port, 60)
    mqttc.publish(HA_DISCOVERY_PREFIX.format(sensor_name), gen_ha_config(mqtt_base_topic, sensor_name))
    mqttc.loop_start()

    while True:
        line = ser.readline().rstrip()
        if len(line) > 0:
            logger.debug("serial received: %s", line)
            mqttc.publish("{}/{}".format(mqtt_base_topic, sensor_name), line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sensor-name", help="name of the sensor device", default="serial")
    parser.add_argument("--serial-port", help="serial port", default="/dev/ttyACM0")
    parser.add_argument("--serial-speed", help="serial Baud rate", type=int, default=115200)
    parser.add_argument("--mqtt-server", help="MQTT server", default="localhost")
    parser.add_argument("--mqtt-port", help="MQTT port", type=int, default=1883)
    parser.add_argument("--mqtt-base-topic", help="MQTT base topic", default=MQTT_BASE_TOPIC)

    args = parser.parse_args()

    main_loop(args.sensor_name, args.serial_port, args.serial_speed, args.mqtt_server, args.mqtt_port, args.mqtt_base_topic)
