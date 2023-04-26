
# Heating circuit monitoring system for Home Assistant using MQTT

[![Stable Release][stable_release]][stable_release]
[![Project Maintenance][maintenance-shield]][user_profile]
[![License][license-shield]](LICENSE)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

Monitoring system for floor heating system circuits. This specific case is created to monitor the heat exchanger circuits for 4 heating loops. 

This system is designed to monitor several different loops in a floor heating system using a heat exchanger. The measured data is published to a Home Assistant using an MQTT broker. 

# Hardware setup

The system is built arround 1-wire temperature sensor DS18B20 connected to a Raspberry Pi with 1-wire setup as default on GPIO 4. 

My specific project will be using 10 DS18B20 sensors to monitor my total 4 loops + supply/return on the heat exchanger. They are connected as shown in this picture:

![Figure 1-1](https://github.com/sldewit/TemperatureMonitor_MQTT/blob/5161e3ec3d567c0ba0c02cbbaa3b987bfebc9c35/Fritzing/Vloerverwarming%20monitor_schema.svg)

Currently the system uses a standard hardcoded setup with fixed Mac Addresses for all sensors. In future expansions the intention is to create this list dynamically and storing it in a config JSON file. 

[buymecoffee]: https://www.buymeacoffee.com/sldewit
[buymecoffeebadge]: https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png
[license-shield]: https://img.shields.io/github/license/sldewit/TemperatureMonitor_MQTT.svg
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40sldewit-blue.svg
[user_profile]: https://github.com/sldewit
[stable_release]: https://shields.io/github/v/release/sldewit/TemperatureMonitor_MQTT?label=stable&sort=semver
