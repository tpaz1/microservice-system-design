import pika, sys, os, time
from send import mail

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
    # rabbitmq connection
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = mail.notification(body)
        if err:
            print(f"error in notification: {err}", flush=True)
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            print(f"notification sent, acknowledging message for queue {os.environ.get('MP3_QUEUE')}", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.queue_declare(queue=os.environ.get("MP3_QUEUE"), durable=True)
    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"), on_message_callback=callback
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