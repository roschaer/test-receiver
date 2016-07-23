#!/usr/bin/env python
import pika
import os
import json
from influxdb import InfluxDBClient

#
# Write values to the influxdb
# Tags: SensorID
# fields: all types defined in the message from rabbitmq
# measurement is called "HackZurich16"
# DB is called "HackZurich16"

def writeInflux(db, msg):
    data = msg['data']
    myPoint = []
    myDB = {}
    myTags = {}
    myFields = {}
    myTags['SensorID']=msg['id']

    for i in range(0,len(data)):
        myFields[data[i]['type']] = data[i]['value']

    myDB['measurement']='HackZurich16'
    myDB['tags']=myTags
    myDB['fields']=myFields
    myPoint.append(myDB)
    json_data = json.dumps(myPoint, sort_keys=True, indent=4, separators=(',', ': '))
    print "[x] Writing Data to InfluxDB"
    db.write_points(myPoint)
#    return myDB

#
# Reading environment variables for the message queue and influxdb
# HOST_INFLUXDB and HOST_RABBITMQ
# not tested yet
host_rabbit = None
host_rabbit = os.environ.get('HOST_RABBITMQ')
if host_rabbit == None:
    print "No Environment Variable HOST_RABBITMQ found, defaulting to 192.168.99.100"
    host_rabbit = "192.168.99.100"
host_influxdb = None
host_influxdb = os.environ.get('HOST_INFLUXDB')
if host_influxdb == None:
    print "No Environment Variable HOST_INFLUXD found, defaulting to 192.168.99.100"
    host_influxdb = "192.168.99.100"

#
# Connecting to RabbitMQ
# and aquire channel "HackZurich16"
#

connection = pika.BlockingConnection(pika.ConnectionParameters(host=host_rabbit))
channel = connection.channel()
channel.queue_declare(queue='HackZurich16')

#
# Connecting to InluxDB
#

db = InfluxDBClient(host_influxdb, "8086", "root", "root", "HackZurich")
db.create_database("HackZurich16")


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    writeInflux(db,json.loads(body))

channel.basic_consume(callback,queue='HackZurich16',no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

