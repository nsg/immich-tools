import time
import os
import string
import random
import threading
import re

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse

from syncthing.api import SyncthingAPI
from syncthing.config import SyncthingConfig

from database import ImmichDatabase

SYNCTHING_CONFIG_PATH = "/var/syncthing/config/config.xml"
SYNCTHING_REST_API_URI = "http://127.0.0.1:8384/rest"

sc = SyncthingConfig(SYNCTHING_CONFIG_PATH)
SYNCTHING_REST_API_KEY = sc.apikey()


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class PendingDevices(threading.Thread):
    def __init__(self, rest_uri: str, api_key: str) -> None:
        super().__init__()
        self.api = SyncthingAPI(rest_uri, api_key)

    def run(self, *args, **kwargs):
        print("Start Pending Devices Service", flush=True)

        while True:
            pending_devices = self.api.get_pending_devices()
            for pending_device_id in pending_devices:
                pending_device_name = pending_devices[pending_device_id]["name"]
                self.api.add_device(pending_device_id, pending_device_name)
                self.api.save_config()

            time.sleep(2)


class PendingFolders(threading.Thread):
    def __init__(self, rest_uri: str, api_key: str) -> None:
        super().__init__()
        self.api = SyncthingAPI(rest_uri, api_key)

    def run(self, *args, **kwargs):
        print("Start Pending Folders Service", flush=True)

        while True:
            pending_folders = self.api.get_pending_folders()
            for folder_id in pending_folders:
                for folder_owner in pending_folders[folder_id]["offeredBy"]:
                    self.api.fetch_config()
                    if folder_id not in self.api.folders():
                        self.api.add_folder(folder_id, folder_owner)
                        self.api.save_config()
            time.sleep(2)


class FileHasher(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.db = ImmichDatabase()

    def run(self, *args, **kwargs):
        print("Start File Hasher Service", flush=True)

        while True:
            time.sleep(2)


db = ImmichDatabase()

time.sleep(3)
api = SyncthingAPI(SYNCTHING_REST_API_URI, SYNCTHING_REST_API_KEY)
api.set_userpass(
    os.getenv("SYNCTHING_USERNAME", random_string()),
    os.getenv("SYNCTHING_PASSWORD", random_string()),
)
api.deny_statistics()
api.remove_folder("default")
api.save_config()

time.sleep(2)

pending_devices = PendingDevices(SYNCTHING_REST_API_URI, sc.apikey())
pending_devices.start()

pending_folders = PendingFolders(SYNCTHING_REST_API_URI, sc.apikey())
pending_folders.start()

file_hasher = FileHasher()
file_hasher.start()

app = FastAPI(
   title="Immich Tools Syncthing Service",
   description="""
       This API wraps and embedded Synthing server. Use this API to
       interact with Syncthing.
   """.strip(),
   version="0.1.0"
)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
   response = RedirectResponse(url='/docs')
   return response

@app.get("/events/disk/{last_seen_id}")
def get_events_disk(last_seen_id: str):
    return api.get_events_disk(since=last_seen_id)

@app.get("/user/{user_id}/{hash}")
def get_local_user_asset(user_id: str, hash: str):
    r = db.local_file(hash, user_id)
    return r

@app.delete("/user/{user_id}/{hash}")
def delete_local_user_asset(user_id: str, hash: str):
    r = db.local_file(hash, user_id)

    if not re.match("^[a-z0-9-]+$", user_id):
        message = {
            "message": "Malformed user_id"
        }
        return JSONResponse(content=message, status_code=401)

    if r['count'] > 1:
        message = {
            "message": "We found more than one match, abort!",
            "response": r
        }
        return JSONResponse(content=message, status_code=401)
    elif r['count'] == 0:
        message = {
            "message": "Hash not found in the database"
        }
        return JSONResponse(content=message, status_code=404)

    path = f"/user/{user_id}/{r['assets'][0]['path']}"

    if not os.path.exists(path):
        message = {
            "message": f"File not found: {path}"
        }
        return JSONResponse(content=message, status_code=404)

    os.unlink(path)

    return {"message": f"File {path} removed"}
