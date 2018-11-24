from kafka import KafkaProducer
import random

producer = KafkaProducer(bootstrap_servers='localhost:9092')

for i in range(50):
    num = str(random.randrange(0, 10))

    producer.send('counter', str.encode(num))

producer.close()
