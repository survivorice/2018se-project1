from kafka import KafkaConsumer

tot = 0
consumer = KafkaConsumer('counter', bootstrap_servers=['localhost:9092'])

for msg in consumer:
    recv = "%s:%d:%d: key=%s value=%s" % (msg.topic, msg.partition, msg.offset, msg.key, msg.value)
    tot += int(msg.value)
    print "The sum of the first ", msg.offset, "received is", tot
