"""Module providing temperature monitoring for multiple temperature sensors to MQTT"""
# pylint: disable=W0703, C0304
import sys
import logging
import json
from threading import Thread, Event
from gpiozero import CPUTemperature
import paho.mqtt.client as mqtt
from pi1wire import Pi1Wire

LOCAL_PATH = "/home/sldewit/Github/TemperatureMonitor_MQTT"
MONITORING_TOPIC = "vloerverwarming/monitoring"

class TemperatureSensor:
    """Class representing a temperature sensor"""
    topic = ""
    tempsensor = 0
    mqtt_broker = mqtt.Client()
    sensor_value = {
        "temperatuur": 0.0
    }
    sensor_attr = {
        "mac_address": "",
        "status": "offline"
    }
    sensor_type = "pi1wire"

    def __init__(self, topic, sensoraddress, mqtt_broker, sensor_type="pi1wire") -> None:
        """Init function"""
        self.topic = topic
        self.mqtt_broker = mqtt_broker
        self.sensor_attr["mac_address"] = sensoraddress
        self.sensor_type = sensor_type
        try:
            if sensor_type == "pi1wire":
                self.tempsensor = Pi1Wire().find(self.sensor_attr["mac_address"])
            if sensor_type == "cpu":
                self.tempsensor = CPUTemperature()
            self.sensor_attr["status"] = "online"
        except Exception as sensor_exception:
            self.sensor_attr["status"] = "offline"
            logging.critical("Exception initializing sensor: %s",sensor_exception)

    def read(self):
        """Sensor read function"""
        if self.tempsensor != 0:
            try:
                if self.sensor_type == "pi1wire":
                    self.sensor_value["temperatuur"] = round(self.tempsensor.get_temperature(),1)
                if self.sensor_type == "cpu":
                    self.sensor_value["temperatuur"] = round(self.tempsensor.temperature,1)
                self.sensor_attr["status"] = "online"
            except Exception as sensor_exception:
                self.sensor_attr["status"] = "offline"
                logging.info("Exception while reading sensor: %s",sensor_exception)
        else: #simulate in case not really there
            self.sensor_attr["status"] = "simulating"
            self.sensor_value["temperatuur"] += 0.1
            logging.info("Simulate sensor: %s - %s", self.topic, self.sensor_value["temperatuur"])

    def publish(self):
        """Sensor publish to MQTT function"""
        logging.info("Publish %s as %s", self.topic, self.sensor_value["temperatuur"])
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

logging.basicConfig(filename=LOCAL_PATH+"/tempmon.log",
                    level=logging.DEBUG,
                    format='%(asctime)s-%(levelname)s:%(message)s')
logging.info('Temperature monitor starting')

try:
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.will_set(MONITORING_TOPIC+'/status', "offline")
    mqtt_client.username_pw_set("mqtt","test_mqtt")
    mqtt_client.connect("192.168.2.209", 1883, 60)
    mqtt_client.publish(MONITORING_TOPIC+'/status',payload = "online", qos=0, retain=True)
    mqtt_client.publish(MONITORING_TOPIC+'/version/installed',payload = "1.0.0", qos=0, retain=True)
    mqtt_client.publish(MONITORING_TOPIC+'/version/latest',payload = "1.0.0", qos=0, retain=True)
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
SENSORS.append(TemperatureSensor('vloerverwarming/monitoring/cputemp',"",mqtt_client,"cpu"))

stop_flag = Event()
thread= MyThread(stop_flag, 10)
thread.start()

logging.info('Temperature monitor started')