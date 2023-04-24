"""Module providing temperature monitoring for multiple temperature sensors to MQTT"""
# pylint: disable=W0703, C0304
import sys
import logging
import json
from threading import Thread, Event
import paho.mqtt.client as mqtt
from pi1wire import Pi1Wire

LOCAL_PATH = "/home/sldewit/Github/TemperatureMonitor_MQTT"

class TemperatureSensor:
    """Class representing a temperature sensor"""
    topic = ""
    temperature = 0.0
    temperaturesensor = 0
    mqtt_broker = mqtt.Client()
    sensor_value = {
        "temperatuur": "0.0"
    }
    sensor_attr = {
        "mac_address": "",
        "status": "offline"
    }


    def __init__(self, topic, sensoraddress, mqtt_broker) -> None:
        """Init function"""
        self.topic = topic
        self.mqtt_broker = mqtt_broker
        self.sensor_attr["mac_address"] = sensoraddress
        try:
            self.temperaturesensor = Pi1Wire().find(self.sensoraddress)
            self.sensor_attr["status"] = "online"
        except Exception as pi1wire_exception:
            self.sensor_attr["status"] = "offline"
            logging.critical("Exception initializing sensor: %s",pi1wire_exception)

    def read(self):
        """Sensor read function"""
        if self.temperaturesensor != 0:
            try:
                self.temperature = round(self.temperaturesensor.get_temperature(),1)
                self.sensor_value["temperatuur"] = str(self.temperature)
                self.sensor_attr["status"] = "online"
            except Exception as sensor_exception:
                self.sensor_attr["status"] = "offline"
                logging.info("Exception while reading sensor: %s",sensor_exception)
        else: #simulate in case not really there
            self.sensor_attr["status"] = "simulating"
            self.temperature += 0.1
            self.sensor_value["temperatuur"] = str(self.temperature)
            logging.info("Simulate sensor: %s - %s", self.topic, self.temperature)

    def publish(self):
        """Sensor publish to MQTT function"""
        logging.info("Publish %s as %s", self.topic, self.temperature)
        try:
            self.mqtt_broker.publish(self.topic,
                                     payload = json.dumps(self.sensor_value, indent=4),
                                     qos=0, retain=True)
            self.mqtt_broker.publish(self.topic+'/attributes',
                                     payload = json.dumps(self.sensor_attr, indent=4),
                                     qos=0,
                                     retain=False)
        except Exception as mqtt_exception:
            logging.critical("MQTT publish failed on topic %s : %s", self.topic, mqtt_exception)

# pylint: disable-next=W0613
def on_connect(client, userdata, flags, return_code):
    """On connect event"""
    if return_code == 0:
        logging.debug("Connected success")
    else:
        logging.critical("Connected fail with code %s", return_code)

class MyThread(Thread):
    """Class for time thread"""
    interval = 1
    def __init__(self, event, interval):
        """Init function"""
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval

    def run(self):
        """Run function of timed thread"""
        while not self.stopped.wait(self.interval):
            for sensor in SENSORS:
                sensor.read()
                sensor.publish()

logging.basicConfig(filename=LOCAL_PATH+"/tempmon.log")
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s-%(levelname)s:%(message)s')
logging.info('Temperature monitor starting')

try:
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.will_set('vloerverwarming/status', "offline")
    mqtt_client.username_pw_set("mqtt","test_mqtt")
    mqtt_client.connect("192.168.2.209", 1883, 60)
    mqtt_client.publish('vloerverwarming/status',payload = "online", qos=0, retain=True)
    mqtt_client.publish('vloerverwarming/version/installed',payload = "1.0.0", qos=0, retain=True)
    mqtt_client.publish('vloerverwarming/version/latest',payload = "1.0.0", qos=0, retain=True)
    mqtt_client.loop_start()
except Exception as connect_exception:
    logging.critical("Failed to connect to MQTT: %s", connect_exception)
    sys.exit()

SENSORS = []

SENSORS.append(TemperatureSensor('vloerverwarming/kring1/aanvoertemp',"28dfc6571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring1/afvoertemp',"28dfd9571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring2/aanvoertemp',"2828ff571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring2/afvoertemp',"28aafd571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring3/aanvoertemp',"28072261300627",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring3/afvoertemp',"280722613294cc",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring4/aanvoertemp',"280722614c7990",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring4/afvoertemp',"280922545d1f8a",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/aanvoertemp',"282bfe571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/afvoertemp',"28092254776424",mqtt_client))

stop_flag = Event()
thread= MyThread(stop_flag, 10)
thread.start()

logging.info('Temperature monitor started')