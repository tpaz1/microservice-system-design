import pika, json, os


def upload(video_file, fs, channel, access):
    try:
        fid = fs.put(video_file)
    except Exception as err:
        print(err, flush=True)
        return "internal server error", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.queue_declare(queue=os.environ.get("VIDEO_QUEUE"), durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("VIDEO_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        print(err, flush=True)
        fs.delete(fid)
        return "internal server error", 500