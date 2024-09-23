import os
import gridfs
import pika
import json
from flask import Flask, request, send_file
from pymongo import MongoClient
from auth_validator import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)

# Connect to MongoDB using pymongo
mongo_client_videos = MongoClient(f"mongodb://{os.environ.get('MONGO_HOST')}:27017/")
mongo_client_mp3s = MongoClient(f"mongodb://{os.environ.get('MONGO_HOST')}:27017/")

mongo_video_db = mongo_client_videos.videos
mongo_mp3_db = mongo_client_mp3s.mp3s

fs_videos = gridfs.GridFS(mongo_video_db)
fs_mp3s = gridfs.GridFS(mongo_mp3_db)

connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ.get("RABBITMQ_HOST")))
channel = connection.channel()


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
            print(err)
            return "internal server error", 500

    return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
