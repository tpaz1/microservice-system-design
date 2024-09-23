import os
import gridfs
import pika
import json
import time
from flask import Flask, request, send_file
from pymongo import MongoClient
from auth_validator import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)

# Retry mechanism for MongoDB connection
def connect_to_mongodb(retries=5, delay=5):
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

# Retry mechanism for RabbitMQ connection
def connect_to_rabbitmq(retries=5, delay=5):
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


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) != 1:
            return "exactly 1 file required", 400
        print(request.files, flush=True)
        for _, video_file in request.files.items():
            err = util.upload(video_file, fs_videos, channel, access)

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err, flush=True)
            return "internal server error", 500

    return "not authorized", 401


if __name__ == "__main__":
    # Connect to MongoDB
    mongo_client_videos = connect_to_mongodb()
    mongo_client_mp3s = connect_to_mongodb()

    mongo_video_db = mongo_client_videos.videos
    mongo_mp3_db = mongo_client_mp3s.mp3s

    fs_videos = gridfs.GridFS(mongo_video_db)
    fs_mp3s = gridfs.GridFS(mongo_mp3_db)

    # Connect to RabbitMQ
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    server.run(host="0.0.0.0", port=8080)
