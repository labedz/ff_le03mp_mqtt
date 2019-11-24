#!/usr/bin/env python

import configparser
import yaml, json
import logging
import threading, signal, time
import sys
import paho.mqtt.client as mqtt
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from datetime import timedelta


Config=configparser.ConfigParser()


def mqtt_on_message(client, userdata, message):
    logging.info("Received message " + str(message.payload) + " on topic "
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
            logging.critical(exc)
    return registers

def get_register(index, modbus_client):
    tries=3

    for read_try in range(tries):
        read_value = modbus_client.read_input_registers(address=index, count=1, unit=1);
        if not read_value.isError():
            logging.debug("Read value %i" % read_value.registers[0])
            return read_value.registers[0]

        logging.info("Doing %i modbus try..." % read_try) 
        time.sleep(1)

    raise ValueError('Error while reading MODBUS message')

def get_registers(registers, modbus_client):
    logging.debug("Fetching register data from metter")
    for type in registers:
        for register in registers[type]:
            if not isinstance(register['index'], list):
                logging.debug("Reading index %i, name: %s" % (register["index"], register["name"]))
                try:
                    register['value'] = float(get_register(register['index'], modbus_client))
                except Exception as e:
                    logging.error("Error while reading register: %s" % e)


            else:
                logging.debug("Reading bound register index %i and %i, name %s" % (register["index"][0], register["index"][1], register["name"]))
                try:
                    value1=float(get_register(register['index'][0], modbus_client))
                    value2=float(get_register(register['index'][1], modbus_client))
                except:
                    logging.error("Error while reading register")

                register["value"]=float(value1 * 256 ** 2 + value2)


def send_message(mqtt_client, topic, payload):
    logging.debug("Sending: topic: %s, payload: %s" % (topic, payload))
    mqtt_client.publish(topic, json.dumps(payload))
#    mqtt_client.publish(topic, "")

def register_services(registers=None, mqtt_client=None):
    logging.info("Registering services")
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
    logging.info("Sending registers values")

    for type in registers:
        msg={}
        for register in registers[type]:
            msg.update({register["value_key"]:  float(register["value"] / register["div"])})

        send_message(
                mqtt_client=mqtt_client,
                topic=register["state_topic"],
                payload=msg
        )

class ProgramKilled(Exception):
    pass

def signal_handler(signum, frame):
    raise ProgramKilled

class SystemdHandler(logging.Handler):
    PREFIX = {
        # EMERG <0>
        # ALERT <1>
        logging.CRITICAL: "<2>",
        logging.ERROR: "<3>",
        logging.WARNING: "<4>",
        # NOTICE <5>
        logging.INFO: "<6>",
        logging.DEBUG: "<7>",
        logging.NOTSET: "<7>"
    }

    def __init__(self, stream=sys.stdout):
        self.stream = stream
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            msg = self.PREFIX[record.levelno] + self.format(record) + "\n"
            self.stream.write(msg)
            self.stream.flush()
        except Exception:
            self.handleError(record)

class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = True
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
                self.stopped.set()
                self.join()
    def run(self):
            while not self.stopped.wait(self.interval.total_seconds()):
                self.execute(*self.args, **self.kwargs)

def update_registers(mqtt_client=None, modbus_client=None, registers=None):
    get_registers(registers, modbus_client)
    send_values(mqtt_client, registers)


def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger=logging.getLogger()
    logger.setLevel("INFO")
    logger.addHandler(SystemdHandler())

    if not Config.read("/usr/local/etc/ff/ff_le03mp_mqtt.ini"):
        logging.error('No config file found')
        sys.exit(1)

    modbus_client = ModbusClient(method="rtu", port=Config['modbus']['port'], timeout=2, stopbits = 2, bytesize = 8,  parity="N", baudrate= 9600)
    modbus_client.connect()

    registers=load_registers_description()
    mqtt_client=mqtt_connect()

    register_services(registers=registers, mqtt_client=mqtt_client)

    job_register = Job(interval=timedelta(seconds=int(Config['default']['register_period'])), execute=register_services, registers=registers, mqtt_client=mqtt_client)
    job_register.start()

    job_update = Job(interval=timedelta(seconds=int(Config['default']['update_period'])), execute=update_registers, mqtt_client=mqtt_client, modbus_client=modbus_client, registers=registers)
    job_update.start()

    while True:
        try:
            time.sleep(60)
        except ProgramKilled:
            logging.info("Program stopped")
            job_register.stop()
            job_update.stop()
            mqtt_client.disconnect()
            break


main()
