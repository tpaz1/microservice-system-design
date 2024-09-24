import smtplib, os, json, sys


def notification(message):
    try:
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]
        receiver_address = message["username"]
        msg = (f"mp3 file_id: {mp3_fid} is now ready!, mail sent to {receiver_address}") 
        print(msg, flush=True)

    except Exception as err:
      print(err)
      return err


# if __name__ == "__main__":
#     try:
#         notification('{"mp3_fid": "1234", "username": "pp"}')
#     except KeyboardInterrupt:
#         print("Interrupted", flush=True)
#         try:
#             sys.exit(0)
#         except SystemExit:
#             os._exit(0)