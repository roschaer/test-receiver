#!/usr/bin/env python
import pika
import os
import json
from influxdb import InfluxDBClient

def writeInflux(db, msg):
#    json_body = [
#        {
#            "measurement": "cpu_load_short",
#            "tags": {
#                "host": "server01",
#                "region": "us-west"
#            },
#            "time": "2009-11-10T23:00:00Z",
#            "fields": {
#                "value": 0.64
#            }
#        }
#    ]
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

host = os.environ.get('HOST_RABBITMQ')
if host == None:
    host_rabbit = "192.168.99.100"
host = os.environ.get('HOST_INFLUXDB')
if host == None:
    host_influxdb = "192.168.99.100"

connection = pika.BlockingConnection(pika.ConnectionParameters(host="192.168.99.100"))
channel = connection.channel()

channel.queue_declare(queue='HackZurich16')

db = InfluxDBClient(host_influxdb, "8086", "root", "root", "HackZurich")
db.create_database("HackZurich16")


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    writeInflux(db,json.loads(body))

channel.basic_consume(callback,queue='HackZurich16',no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

