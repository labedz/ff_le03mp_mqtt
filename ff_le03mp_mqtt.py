#!/usr/bin/env python

import time
import json
import paho.mqtt.client as mqtt
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

modbus_client = ModbusClient(method='rtu', port='/dev/ttyUSB0', timeout=1, stopbits = 2, bytesize = 8,  parity='N', baudrate= 9600)
modbus_client.connect()

def mqtt_on_message(client, userdata, message):
    print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))

mqtt_host = '10.40.1.87'
auth = {
    'username': 'hass',
    'password': 'BuB1xC6srh8W',
}

mqtt_client=mqtt.Client('le03mp')
mqtt_client.username_pw_set(auth['username'], auth['password'])
mqtt_client.on_message=mqtt_on_message
mqtt_client.connect(mqtt_host, 1883)


state_topic = 'homeassistant/sensor/le03mp_bound/state'
le3mp_bound_registers = [
        {'indexes': [20, 21], 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_kwh/config", 'state_topic': "%s" % state_topic, 'value_key': "power_consumed", 'value_template': "{{ value_json.power_consumed}}", 'unit': "kWh", 'device_class': 'power', 'name': 'Power consumed'},
        {'indexes': [22, 23], 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_kvarh/config", 'state_topic': "%s" % state_topic, 'value_key': "reactive_power_consumed", 'value_template': "{{ value_json.reactive_power_consumed}}", 'unit': "kvarh", 'device_class': 'reactivr_power', 'name': 'Reactive power consumed'}
]

state_topic = 'homeassistant/sensor/le03mp_voltage/state'
le3mp_registers_voltage = [
        {'index': 1, 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_v_l1/config", 'state_topic': "%s" % state_topic, 'value_key': "l1_voltage", 'value_template': "{{ value_json.l1_voltage}}", 'unit': "V", 'device_class': 'voltage', 'name': 'l1 Voltage'},
        {'index': 2, 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_v_l2/config", 'state_topic': "%s" % state_topic, 'value_key': "l2_voltage", 'value_template': "{{ value_json.l2_voltage}}", 'unit': "V", 'device_class': 'voltage', 'name': 'l2 Voltage'},
        {'index': 3, 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_v_l3/config", 'state_topic': "%s" % state_topic, 'value_key': "l3_voltage", 'value_template': "{{ value_json.l3_voltage}}", 'unit': "V", 'device_class': 'voltage', 'name': 'l3 Voltage'}
        ]

state_topic = 'homeassistant/sensor/le03mp_current/state'
le3mp_registers_current = [
        {'index': 4, 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_A_l1/config", 'state_topic': "%s" % state_topic, 'value_key': "l1_current", 'value_template': "{{ value_json.l1_current}}", 'unit': "A", 'device_class': 'current', 'name': 'l1 Current'},
        {'index': 5, 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_A_l2/config", 'state_topic': "%s" % state_topic, 'value_key': "l2_current", 'value_template': "{{ value_json.l2_current}}", 'unit': "A", 'device_class': 'current', 'name': 'l2 Current'},
        {'index': 6, 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_A_l3/config", 'state_topic': "%s" % state_topic, 'value_key': "l3_current", 'value_template': "{{ value_json.l3_current}}", 'unit': "A", 'device_class': 'current', 'name': 'l3 Current'}
        ]

state_topic = 'homeassistant/sensor/le03mp_power/state'
le3mp_registers_power = [
        {'index': 7, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_kw_l1/config", 'state_topic': "%s" % state_topic, 'value_key': "l1_power", 'value_template': "{{ value_json.l1_power}}", 'unit': "kW", 'device_class': 'power', 'name': 'l1 Power'},
        {'index': 8, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_kw_l2/config", 'state_topic': "%s" % state_topic, 'value_key': "l2_power", 'value_template': "{{ value_json.l2_power}}", 'unit': "kW", 'device_class': 'power', 'name': 'l2 Power'},
        {'index': 9, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_kw_l3/config", 'state_topic': "%s" % state_topic, 'value_key': "l3_power", 'value_template': "{{ value_json.l3_power}}", 'unit': "kW", 'device_class': 'power', 'name': 'l3 Power'},
        {'index': 10, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_kw/config", 'state_topic': "%s" % state_topic, 'value_key': "power", 'value_template': "{{ value_json.power}}", 'unit': "kW", 'device_class': 'power', 'name': 'Sum Power'},
        {'index': 24, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_kvar_l1/config", 'state_topic': "%s" % state_topic, 'value_key': "l1_reactive_power", 'value_template': "{{ value_json.l1_reactive_power}}", 'unit': "kvar", 'device_class': 'reactive_power', 'name': 'l1 reactive power'},
        {'index': 25, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_kvar_l2/config", 'state_topic': "%s" % state_topic, 'value_key': "l2_reactive_power", 'value_template': "{{ value_json.l2_reactive_power}}", 'unit': "kvar", 'device_class': 'reactive_power', 'name': 'l2 reactive power'},
        {'index': 26, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_kvar_l3/config", 'state_topic': "%s" % state_topic, 'value_key': "l3_reactive_power", 'value_template': "{{ value_json.l3_reactive_power}}", 'unit': "kvar", 'device_class': 'reactive_power', 'name': 'l3 reactive power'},
        {'index': 27, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_kvaar/config", 'state_topic': "%s" % state_topic, 'value_key': "reactive_power", 'value_template': "{{ value_json.reactive_power}}", 'unit': "kvar", 'device_class': 'power', 'name': 'Reactive power'}
         ]

state_topic = 'homeassistant/sensor/le03mp_misc/state'
le3mp_registers_misc = [
       {'index': 15, 'div': 100, 'config_topic': "homeassistant/sensor/le03mp_hz/config", 'state_topic': "%s" % state_topic, 'value_key': "freq", 'value_template': "{{ value_json.freq}}", 'unit': "Hz", 'device_class': 'frequency', 'name': 'Frequency'},
       {'index': 30, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_l1_cosa/config", 'state_topic': "%s" % state_topic, 'value_key': "l1_cosa", 'value_template': "{{ value_json.l1_cosa}}", 'unit': "unit", 'device_class': 'power', 'name': 'l1 power factor'},
        {'index': 31, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_l2_cosa/config", 'state_topic': "%s" % state_topic, 'value_key': "l2_cosa", 'value_template': "{{ value_json.l2_cosa}}", 'unit': "unit", 'device_class': 'power', 'name': 'l2 power factor'},
        {'index': 32, 'div': 1000, 'config_topic': "homeassistant/sensor/le03mp_l3_cosa/config", 'state_topic': "%s" % state_topic, 'value_key': "l3_cosa", 'value_template': "{{ value_json.l3_cosa}}", 'unit': "unit", 'device_class': 'power', 'name': 'l3 power factor'}
]


def get_registers():
    print("Fetching register data from metter")
    for register in le3mp_registers_voltage:
        read_value = modbus_client.read_input_registers(address=register['index'], count=1, unit=1);
        register['value'] = float(read_value.registers[0])
        print("Fetched value: %f" % register['value'])
    for register in le3mp_registers_current:
        read_value = modbus_client.read_input_registers(address=register['index'], count=1, unit=1);
        register['value'] = float(read_value.registers[0])
        print("Fetched value: %f" % register['value'])
    for register in le3mp_registers_power:
        read_value = modbus_client.read_input_registers(address=register['index'], count=1, unit=1);
        register['value'] = float(read_value.registers[0])
        print("Fetched value: %f" % register['value'])
    for register in le3mp_registers_misc:
        read_value = modbus_client.read_input_registers(address=register['index'], count=1, unit=1);
        register['value'] = float(read_value.registers[0])
        print("Fetched value: %f" % register['value'])

def get_bound_registers():
    print("Fetching bound register data from metter")
    for register in le3mp_bound_registers:
        read_value1 = modbus_client.read_input_registers(address=register['indexes'][0], count=1, unit=1);
        read_value2 = modbus_client.read_input_registers(address=register['indexes'][1], count=1, unit=1);
        register['value']=float(read_value1.registers[0] * 256 ** 2 + read_value2.registers[0])
        print("Fetched values 1: %f, 2: %f, which gives: %f" % (read_value1.registers[0],read_value2.registers[0], register['value']))


def send_message(topic, payload):
    print("Sending: topic: %s, payload: %s" % (topic, payload))
    mqtt_client.publish(topic, json.dumps(payload))
#    mqtt_client.publish(topic, '')

def register_services():
    print("Registering services")
    for register in le3mp_registers_voltage:
        send_message(
                topic=register['config_topic'],
                payload={
                    'name': register['name'],
                    'state_topic': register['state_topic'],
                    'unit_of_measurement': register['unit'],
                    'value_template': register['value_template']
                    }
                )

    for register in le3mp_registers_current:
        send_message(
                topic=register['config_topic'],
                payload={
                    'name': register['name'],
                    'state_topic': register['state_topic'],
                    'unit_of_measurement': register['unit'],
                    'value_template': register['value_template']
                    }
                )

    for register in le3mp_registers_power:
        send_message(
                topic=register['config_topic'],
                payload={
                    'name': register['name'],
                    'state_topic': register['state_topic'],
                    'unit_of_measurement': register['unit'],
                    'value_template': register['value_template']
                    }
                )
    for register in le3mp_registers_misc:
        send_message(
                topic=register['config_topic'],
                payload={
                    'name': register['name'],
                    'state_topic': register['state_topic'],
                    'unit_of_measurement': register['unit'],
                    'value_template': register['value_template']
                    }
                )
    for register in le3mp_bound_registers:
        send_message(
                topic=register['config_topic'],
                payload={
                    'name': register['name'],
                    'state_topic': register['state_topic'],
                    'unit_of_measurement': register['unit'],
                    'value_template': register['value_template']
                    }
                )

def send_values():
    messages=[]
    print("Sending values")

    msg={}
    for register in le3mp_registers_voltage:
        msg.update({register['value_key']:  float(register['value'] / register['div'])})
    send_message(
            topic=register['state_topic'],
            payload=msg
            )

    msg={}
    for register in le3mp_registers_current:
        msg.update({register['value_key']:  float(register['value'] / register['div'])})
    send_message(
            topic=register['state_topic'],
            payload=msg
            )

    msg={}
    for register in le3mp_registers_power:
        msg.update({register['value_key']:  float(register['value'] / register['div'])})
    send_message(
            topic=register['state_topic'],
            payload=msg
            )

    msg={}
    for register in le3mp_registers_misc:
        msg.update({register['value_key']:  float(register['value'] / register['div'])})
    send_message(
            topic=register['state_topic'],
            payload=msg
            )

    msg={}
    for register in le3mp_bound_registers:
        msg.update({register['value_key']:  float(register['value'] / register['div'])})
    send_message(
            topic=register['state_topic'],
            payload=msg
            )


register_services()
while True:
    get_registers()
    get_bound_registers()
    send_values()
    time.sleep(60)

mqtt_client.disconnect()
