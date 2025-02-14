#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import threading
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer
import os
import json
from pymongo import MongoClient


# In[ ]:


# Define Kafka configuration
kafka_config = {
    'bootstrap.servers': 'pkc-l7pr2.ap-south-1.aws.confluent.cloud:9092',
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'KKD5RSXIDOZ3IOCX',
    'sasl.password': '/mR8K0JeGDjZgqmO59Efhaumm+NsGyiVvXZskRY7iJ0ZznY7+wn9Q1YX+vCSFALK',
    'group.id': 'group11',
    'auto.offset.reset': 'earliest'
}


# In[ ]:


# Create a Schema Registry client
schema_registry_client = SchemaRegistryClient({
    'url': 'https://psrc-9jzo5.us-central1.gcp.confluent.cloud',
    'basic.auth.user.info': '{}:{}'.format('QNKVOHE34H7CE3NQ', 'D1ltpZHhQFvHAOn9GM+AQosxZ6YLyN6sg8w4RvsCBS2SATbbD77orTbiHG5iLnkw')
})

# Fetch the latest Avro schema for the value
subject_name = 'logistics_data-value'
schema_str = schema_registry_client.get_latest_version(subject_name).schema.schema_str

# Create Avro Deserializer for the value
key_deserializer = StringDeserializer('utf_8')
avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)


# In[ ]:


# MongoDB configuration
mongo_client = MongoClient('mongodb+srv://Anusha:Kunapuli123@mongo-db-cluster.oh44z.mongodb.net/')  # Replace with your MongoDB connection string
db = mongo_client['gds_db']  # Replace with your database name
collection = db['logistics_data']  # Replace with your collection name


# In[ ]:


# Define the DeserializingConsumer
consumer = DeserializingConsumer({
    'bootstrap.servers': kafka_config['bootstrap.servers'],
    'security.protocol': kafka_config['security.protocol'],
    'sasl.mechanisms': kafka_config['sasl.mechanisms'],
    'sasl.username': kafka_config['sasl.username'],
    'sasl.password': kafka_config['sasl.password'],
    'key.deserializer': key_deserializer,
    'value.deserializer': avro_deserializer,
    'group.id': kafka_config['group.id'],
    'auto.offset.reset': kafka_config['auto.offset.reset']
})

# Subscribe to the 'logistic_data' topic
consumer.subscribe(['logistics_data'])


# In[ ]:


# Process and insert Avro messages into MongoDB
try:
    while True:
        msg = consumer.poll(1.0)  # Adjust the timeout as needed

        if msg is None:
            continue
        if msg.error():
            print('Consumer error: {}'.format(msg.error()))
            continue

        # Deserialize Avro data
        value = msg.value()
        print("Received message:", value)
        
        # Data validation checks
        if 'bookingID' not in value or value['bookingID'] is None:
            print("Skipping message due to missing or null 'bookingID'.")
            continue

        # Data type validation checks
        if not isinstance(value['bookingID'], str):
            print("Skipping message due to 'bookingID' not being a string.")
            continue
        
        #We can add more checks as needed but this is just a demo
        
        # Check if a document with the same 'bookingID' exists
        existing_document = collection.find_one({'bookingID': value['bookingID']})

        if existing_document:
            print(f"Document with bookingID '{value['bookingID']}' already exists. Skipping insertion.")
        else:
            # Insert data into MongoDB
            collection.insert_one(value)
            print("Inserted message into MongoDB:", value)


except KeyboardInterrupt:
    pass
finally:
    # Commit the offset to mark the message as processed
    consumer.commit()
    consumer.close()
    mongo_client.close()


# In[ ]:




