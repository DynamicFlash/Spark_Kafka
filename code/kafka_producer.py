from confluent_kafka import Producer
import os
from time import sleep
from json import dumps

CLOUDKARAFKA_BROKERS = 'kafkabroker1:port,kafkabroker2:port,kafkabroker3:port'
CLOUDKARAFKA_USERNAME = "karafka_username"
CLOUDKARAFKA_PASSWORD ="karafka_password"
CLOUDKARAFKA_TOPIC = "karafka_username-default"
DELAY = 3

#Setting configuration parameters
'''
security.protocol: security protocol to use
sasl.mechanisms: authetication mechanisms to be used
sasl.username: username as specified in cloud Karakfa dashboard,
sasl.password: password as specified in cloud Karakfa dashboard
'''
producer_conf = {
    'bootstrap.servers': CLOUDKARAFKA_BROKERS,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'SCRAM-SHA-256',
    'sasl.username': CLOUDKARAFKA_USERNAME,
    'sasl.password': CLOUDKARAFKA_PASSWORD
}

prod = Producer(**producer_conf)

#acknowledgement callback function
def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))


#Get data to be streamed
import urllib.request as request

url ="https://www.gutenberg.org/ebooks/67404.txt.utf-8"
request.urlretrieve(url, 'book.txt')

#data to be streamed through kafka
file1 = open('book.txt', 'r', encoding='utf-8')
lines = file1.readlines()
count = 0


try:
    for line in lines:
        sleep(DELAY)
        line = line.strip()

        if line:
            prod.produce(CLOUDKARAFKA_TOPIC, value=line.encode('utf-8'), callback=acked)
            count+=1

        if count>100:
            break

        prod.poll(1)
        
except BufferError as e:
    print('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                     len(prod))


