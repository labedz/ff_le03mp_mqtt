# MQTT gateway for FF LE03MP energy metter

Fetch FF LE03MP energy metter data and push it to MQTT for home assistant
like software.

## Installing

Create config ff_le03mp_mqtt.ini file using template:

```
[default]
register_file=/usr/local/etc/ff/registers.yaml
register_period=300
update_period=60

[mqtt]
host=<HOST>
port=<PORT>
username=<MQTT_USERNAME>
password=<MQTT_PASSWORD>
client_name="le03mp"

[modbus]
port=/dev/ttyUSB0

```

Copy script and configs to destination directory like /usr/local/

```
git clone http://github.com/labedz/ff_le03mp_mqtt.git
sudo cp ff_le03mp_mqtt.py /usr/local/bin/
sudo cp ff_le03mp_mqtt.ini /usr/local/etc/ff/
sudo cp registers.yaml /usr/local/etc/ff/
```

Copy systemd service file:

```
sudo cp le03mp_mqtt_gateway.service /lib/systemd/system
```


Enable and restart service
```
sudo systemctl daemon-reload
sudo systemctl enable le03mp_mqtt_gateway
```

