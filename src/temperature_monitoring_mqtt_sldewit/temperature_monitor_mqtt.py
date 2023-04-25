"""Module providing temperature monitoring for multiple temperature sensors to MQTT"""
# pylint: disable=W0703, W0613, C0304, C0301, R0902, R0903
import sys
import logging
import json
from threading import Thread, Event
from gpiozero import CPUTemperature
import paho.mqtt.client as mqtt
from pi1wire import Pi1Wire

LOCAL_PATH = "/home/sldewit/Github/TemperatureMonitor_MQTT"
MONITORING_TOPIC = "vloerverwarming/monitoring"

mqtt_client = mqtt.Client()

class MQTTDevice:
    """Class representing MQTT device"""
    def __init__(self, identifiers, model, name, via_device) -> None:
        """Init function"""
        self.identifiers = identifiers
        self.manufacturer = "White Inc"
        self.model = model
        self.name = name
        self.via_device = via_device
        self.sw_version = "1.0"

class MQTTConfig:
    """Class representing MQTT config"""
    def __init__(self, topic, kring, meetpunt, sensor_type="pi1wire") -> None:
        """Init function"""
        self.unit_of_meas = "°C"
        self.val_tpl = "{{ value_json.temperature }}"
        self.dev_cla = "temperature"
        self.avty_t = "vloerverwarming/monitoring/status"
        if sensor_type == "pi1wire":
            if kring > 0:
                self.name = f"Vloerverwarming {meetpunt} kring {kring}"
                self.stat_t = topic
                self.uniq_id = f"kring{kring}-{meetpunt}temp"
                self.json_attr_t = topic+"/attributes"
                identifiers = [f"kring{kring}"]
                model = "DS18B20"
                name = f"Kring {kring}"
                via_device = "vloerverwarming"
                self.dev = MQTTDevice(identifiers, model, name, via_device)
            else:
                self.name = f"Vloerverwarming {meetpunt}"
                self.stat_t = topic
                self.uniq_id = f"{meetpunt}temp"
                self.json_attr_t = topic+"/attributes"
                identifiers = ["vloerverwarming"]
                model = "DS18B20"
                name = "Vloerverwarming"
                via_device = ""
                self.dev = MQTTDevice(identifiers, model, name, via_device)
        else:
            self.name = f"Monitoring {meetpunt}"
            self.stat_t = topic
            self.uniq_id = f"{meetpunt}-temp"
            self.json_attr_t = topic+"/attributes"
            identifiers = ["monitoring"]
            model = "Raspberry Pi"
            name = "Monitoring"
            via_device = "vloerverwarming"
            self.dev = MQTTDevice(identifiers, model, name, via_device)

class SensorValue:
    """Class representing sensor value"""
    temperature = 0.0
    def __init__(self, temperature):
        """Init function"""
        self.temperature = temperature

    def get(self):
        """Get temperature function"""
        return self.temperature

    def set(self, temperature):
        """Set temperature function"""
        self.temperature = round(temperature,1)

class SensorAttr:
    """Class representing sensor attributes"""
    def __init__(self, mac_address, status):
        """Init function"""
        self.mac_address = mac_address
        self.status = status

    def set_mac_address(self, mac_address):
        """Set mac address function"""
        self.mac_address = mac_address

    def get_mac_address(self):
        """Get mac address function"""
        return self.mac_address

class TemperatureSensor:
    """Class representing a temperature sensor"""
    def __init__(self, kring, meetpunt, sensor_address, sensor_type="pi1wire") -> None:
        """Init function"""
        if sensor_type == "pi1wire":
            if kring > 0:
                self.topic = f"vloerverwarming/kring{kring}/{meetpunt}temp"
                self.cfg_topic = f"homeassistant/sensor/kring{kring}_{meetpunt}temperatuur/config"
            else:
                self.topic = f"vloerverwarming/{meetpunt}temp"
                self.cfg_topic = f"homeassistant/sensor/{meetpunt}temperatuur/config"
        if sensor_type == "cpu":
            self.topic = f"vloerverwarming/monitoring/{meetpunt}temp"
            self.cfg_topic = f"homeassistant/sensor/{meetpunt}temperatuur/config"
        self.sensor_config = MQTTConfig(self.topic, kring, meetpunt, sensor_type)
        self.mqtt_broker = mqtt_client
        self.sensor_attr = SensorAttr(sensor_address, "offline")
        self.sensor_value = SensorValue(0.0)
        self.sensor_type = sensor_type
        self.config_set = False
        try:
            if sensor_type == "pi1wire":
                self.tempsensor = Pi1Wire().find(self.sensor_attr.mac_address)
            if sensor_type == "cpu":
                self.tempsensor = CPUTemperature()
            self.sensor_attr.status = "online"
        except Exception as sensor_exception:
            self.sensor_attr.status = "offline"
            logging.critical("Exception initializing sensor: %s",sensor_exception)

    def publish_config(self):
        """Publish config to MQTT broker"""
        try:
            self.mqtt_broker.publish(self.cfg_topic,
                                     payload = json.dumps(self.sensor_config,
                                                          default=lambda o:o.__dict__,
                                                          indent=4),
                                     qos=0, retain=True)
            self.config_set = True
        except Exception as mqtt_exception:
            logging.critical("MQTT publish failed on topic %s : %s", self.cfg_topic, mqtt_exception)

    def read(self):
        """Sensor read function"""
        if self.tempsensor != 0:
            try:
                if self.sensor_type == "pi1wire":
                    self.sensor_value.set(self.tempsensor.get_temperature())
                if self.sensor_type == "cpu":
                    self.sensor_value.set(self.tempsensor.temperature)
                self.sensor_attr.status = "online"
            except Exception as sensor_exception:
                self.sensor_attr.status = "offline"
                logging.debug("Exception while reading sensor: %s",sensor_exception)
        else: #simulate in case not really there
            self.sensor_attr.status = "simulating"
            self.sensor_value.temperature += 0.1
            logging.debug("Simulate sensor: %s - %s", self.topic, self.sensor_value.temperature)

    def publish(self):
        """Sensor publish to MQTT broker"""
        logging.debug("Publish %s as %s", self.topic, self.sensor_value.__dict__)
        if not self.config_set:
            self.publish_config()
        try:
            self.mqtt_broker.publish(self.topic,
                                     payload = json.dumps(self.sensor_value.__dict__, indent=4),
                                     qos=0, retain=True)
            self.mqtt_broker.publish(self.topic+'/attributes',
                                     payload = json.dumps(self.sensor_attr.__dict__, indent=4),
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
                    level=logging.INFO,
                    format='%(asctime)s-%(levelname)s:%(message)s')
logging.debug('Temperature monitor starting')

try:
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

SENSORS.append(TemperatureSensor(0, "cpu","","cpu"))
SENSORS.append(TemperatureSensor(0, "aanvoer","282bfe571f64ff"))
SENSORS.append(TemperatureSensor(0, "afvoer","28092254776424"))
SENSORS.append(TemperatureSensor(1, "aanvoer","28dfc6571f64ff"))
SENSORS.append(TemperatureSensor(1, "afvoer","28dfd9571f64ff"))
SENSORS.append(TemperatureSensor(2, "aanvoer","2828ff571f64ff"))
SENSORS.append(TemperatureSensor(2, "afvoer","28aafd571f64ff"))
SENSORS.append(TemperatureSensor(3, "aanvoer","28072261300627"))
SENSORS.append(TemperatureSensor(3, "afvoer","280722613294cc"))
SENSORS.append(TemperatureSensor(4, "aanvoer","280722614c7990"))
SENSORS.append(TemperatureSensor(4, "afvoer","280922545d1f8a"))

stop_flag = Event()
thread= MyThread(stop_flag, 10)
thread.start()

logging.debug('Temperature monitor started')