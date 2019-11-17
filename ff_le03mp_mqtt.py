#!/usr/bin/env python

import json
import configparser
import time
import yaml
import paho.mqtt.client as mqtt
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

Config=configparser.ConfigParser()
Config.read("ff_le03mp_mqtt.ini")

modbus_client = ModbusClient(method="rtu", port=Config['modbus']['port'], timeout=2, stopbits = 2, bytesize = 8,  parity="N", baudrate= 9600)
modbus_client.connect()

def mqtt_on_message(client, userdata, message):
    print("Received message " + str(message.payload) + " on topic "
        + message.topic + " with QoS " + str(message.qos))


def mqtt_connect():
    mqtt_client=mqtt.Client(Config['mqtt']['client_name'])
    mqtt_client.username_pw_set(Config['mqtt']['username'], Config['mqtt']['password'])
    mqtt_client.on_message=mqtt_on_message
    mqtt_client.connect(Config['mqtt']['host'], int(Config['mqtt']['port']))
    return mqtt_client

def load_registers_description():
    with open(Config['default']['register_file'], 'r') as stream:
        try:
            registers=yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return registers

def get_register(index):
    tries=3

    for read_try in range(tries):
        read_value = modbus_client.read_input_registers(address=index, count=1, unit=1);
        if not read_value.isError():
            return read_value.registers[0]

        print("Doing %i modbus try..." % read_try) 
        time.sleep(1)

    raise ValueError('Error while reading MODBUS message')

def get_registers(registers):
    print("Fetching register data from metter")
    for type in registers:
        for register in registers[type]:
            if not isinstance(register['index'], list):
                print("Reading index %i" % register["index"])
                try:
                    register['value'] = float(get_register(register['index']))
                except:
                    print("Error while reading register")


            else:
                print("Reading bound register index %i and %i" % (register["index"][0], register["index"][1]))
                try:
                    value1=float(get_register(register['index'][0]))
                    value2=float(get_register(register['index'][1]))
                except:
                    print("Error while reading register")

                register["value"]=float(value1 * 256 ** 2 + value2)


def send_message(mqtt_client, topic, payload):
    print("Sending: topic: %s, payload: %s" % (topic, payload))
    mqtt_client.publish(topic, json.dumps(payload))
#    mqtt_client.publish(topic, "")

def register_services(registers, mqtt_client):
    print("Registering services")
    for type in registers:
        for register in registers[type]:
            send_message(
                    mqtt_client=mqtt_client,
                    topic=register["config_topic"],
                    payload={
                        "name": register["name"],
                        "state_topic": register["state_topic"],
                        "unit_of_measurement": register["unit"],
                        "value_template": register["value_template"]
                        }
                    )

def send_values(mqtt_client, registers):
    messages=[]
    print("Sending values")

    for type in registers:
        msg={}
        for register in registers[type]:
            msg.update({register["value_key"]:  float(register["value"] / register["div"])})

        send_message(
                mqtt_client=mqtt_client,
                topic=register["state_topic"],
                payload=msg
        )



registers=load_registers_description()
mqtt_client=mqtt_connect()
register_services(registers, mqtt_client)
while True:
    get_registers(registers)
    send_values(mqtt_client, registers)
    time.sleep(60)

mqtt_client.disconnect()
