import json

class sensor_config:
    name = ""
    MQTT_Topic = ""
    mac_address = ""

    def __init__(self, name, mqtt_topic, mac_address) -> None:
        self.name = name
        self.MQTT_Topic = mqtt_topic
        self.mac_address = mac_address

class ha_config:
    def __init__(self, name, mqtt_topic, mac_address) -> None:
        self.name = name
        self.unit_of_meas = "°C"
        self.stat_t = mqtt_topic
        self.uniq_id = mac_address
        self.val_tpl = "{{ value_json.temperatuur }}"
        self.dev_cla = "temperature"
        self.avty_t = "vloerverwarming/status"


class MySensor:
    config = ""
    ha_conf = ""
    value = 2.2
    
    def __init__(self, name, mqtt_topic, mac_address) -> None:
        self.config = sensor_config(name, mqtt_topic, mac_address)
        self.ha_conf = ha_config(name, mqtt_topic, mac_address)

SENSORS = []

SENSORS.append(MySensor("", "", "28dfc6571f64ff"))
SENSORS.append(MySensor("", "", "28dfd9571f64ff"))
SENSORS.append(MySensor("", "", "2828ff571f64ff"))
SENSORS.append(MySensor("", "", "28aafd571f64ff"))
SENSORS.append(MySensor("", "", "282bfe571f64ff"))
SENSORS.append(MySensor("", "", "282bfe576f64ff"))


print("Read back file...")
try:
    with open("./drafts/TestJSON/sensor_list.json", "r") as readfile:
        json_read_sensor_list = json.load(readfile)
        sensor_counter = 0
        for item in json_read_sensor_list:
            print(item)
            sensor_found = False
            for sensor in SENSORS:
                if sensor.config.mac_address == str(item['mac_address']):
                    sensor.config.name = str(item['name'])
                    sensor.config.MQTT_Topic = str(item['MQTT_Topic'])
                    sensor_found = True
            if sensor_found == False:
                new_sensor_name = str(item['name'])
                new_sensor_MQTT_Topic = str(item['MQTT_Topic'])
                new_sensor_mac_address = str(item['mac_address'])
                SENSORS.append(MySensor(new_sensor_name, new_sensor_MQTT_Topic, new_sensor_mac_address))
except FileNotFoundError as ReadFileError:
    print(ReadFileError)

json_sensor_list = json.dumps([sensor.config.__dict__ for sensor in SENSORS], indent=4)
print(json_sensor_list)

try:
    with open("./drafts/TestJSON/sensor_list.json", "w") as outfile:
        outfile.write(json_sensor_list)
except FileNotFoundError as WriteFileError:
    print(WriteFileError)

print(SENSORS[0].ha_conf.__dict__)