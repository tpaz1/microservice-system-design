import pika
import sys
import os
import time
from pymongo import MongoClient
import gridfs
from convert import to_mp3


def connect_to_mongodb(retries=5, delay=5):
    """Establish a connection to MongoDB with retry logic."""
    client = None
    for attempt in range(retries):
        try:
            client = MongoClient(f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@{os.environ.get('MONGO_HOST')}:27017/")
            print(f"Connected to MongoDB on attempt {attempt + 1}", flush=True)
            break
        except Exception as e:
            print(f"Failed to connect to MongoDB (attempt {attempt + 1}/{retries}): {e}", flush=True)
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise Exception("Failed to connect to MongoDB after multiple attempts")

    return client


def connect_to_rabbitmq(retries=5, delay=5):
    """Establish a connection to RabbitMQ with retry logic."""
    connection = None
    for attempt in range(retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(os.environ.get("RABBITMQ_HOST"))
            )
            print(f"Connected to RabbitMQ on attempt {attempt + 1}", flush=True)
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{retries}): {e}", flush=True)
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise Exception("Failed to connect to RabbitMQ after multiple attempts")

    return connection


def main():
    # Connect to MongoDB
    client = connect_to_mongodb()
    db_videos = client.videos
    db_mp3s = client.mp3s

    # Initialize GridFS
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # Connect to RabbitMQ
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            print(f"error in convert: {err}", flush=True)
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            print(f"notification sent, acknowledging message for queue {os.environ.get('VIDEO_QUEUE')}", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.queue_declare(queue=os.environ.get("VIDEO_QUEUE"), durable=True)
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C", flush=True)

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted", flush=True)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
