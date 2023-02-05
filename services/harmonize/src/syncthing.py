import os
import requests
import threading
import time
import hashlib
from datetime import datetime

import harmonize
from harmonize import Types


def hash_file(path):
    file_hash = hashlib.sha1()
    with open(path, "rb") as f:
        fb = f.read(2048)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(2048)
    return file_hash.hexdigest()


def parse_nanodate(s):
    s = s.split(".")[0]
    return datetime.strptime(f"{s}", "%Y-%m-%dT%H:%M:%S")


class SyncthingAPI:

    settings: harmonize.Settings

    def __init__(self, settings: harmonize.Settings) -> None:
        self.settings = settings

    def get(self, url):
        return self.req(url).json()

    def put(self, url, data):
        return self.req(url, put=True, data=data)

    def req(self, url, put=False, data={}):

        req_url = f"{self.settings.syncthing_url}/{url}"
        headers = {"X-API-Key": self.settings.syncthing_apikey}

        if put:
            r = requests.put(req_url, headers=headers, json=data)
        else:
            r = requests.get(req_url, headers=headers)

        if r.status_code != 200:
            raise Exception(f"Syncthing API returned {r.status_code}. {r.content}")

        return r

    def get_events_disk(self, since=None):
        if since:
            url = f"events/disk?since={since}"
        else:
            url = f"events/disk"

        return self.get(url)

    def has_remote_folder(self, folder_id):
        sy_folders = [x["id"] for x in self.fetch_config()["folders"]]
        return folder_id in sy_folders

    def has_local_folder(self):
        return os.path.exists(self.settings.syncthing_local_dir)

    def fetch_config(self):
        return self.get("config")

    def push_config(self, config):
        return self.put("config", config)


class SynthingThread(threading.Thread):

    settings: harmonize.Settings
    queue: harmonize.HarmonizeQueue
    syncthing: SyncthingAPI

    def __init__(self, settings: harmonize.Settings, queue: harmonize.HarmonizeQueue) -> None:
        super().__init__()
        self.settings = settings
        self.queue = queue
        self.syncthing = SyncthingAPI(settings)

        folder_id = settings.syncthing_folder_id

        if not self.syncthing.has_remote_folder(folder_id):
            harmonize.fail(
                f"Error, folder with folder_id {folder_id} not found in Syncthing"
            )

        if not self.syncthing.has_local_folder():
            harmonize.fail("Syncthing local folder do not exist")

    def run(self, *args, **kwargs):
        harmonize.log("Syncthing thread started")

        last_seen_id = None
        while True:
            for event in self.syncthing.get_events_disk(since=last_seen_id):
                self.tick(event)
            last_seen_id = event.get("id")

            time.time(10)

    def tick(self, event):

        # Only listen on events from SYNCTHING_FOLDER_ID
        if event["data"]["folder"] == self.settings.syncthing_folder_id:

            event_ts = parse_nanodate(event["time"]).timestamp()
            action = event["data"]["action"]
            modby = event["data"]["modifiedBy"]
            file = event["data"]["path"]

            # Only process events in the future
            if event_ts < self.settings.program_start_ts:
                return

            # Ignore non-files (like directories)
            if event["data"]["type"] != "file":
                return

            # Ignore hidden images (for example trashed files)
            if file[0] == ".":
                return

            # Example: image created and/or deleted on the phone
            if event["type"] == "RemoteChangeDetected":

                # Set path to the local files
                if action == "deleted":
                    local_path = (
                        f"{self.settings.syncthing_local_dir}/.stversions/{file}"
                    )
                else:
                    local_path = f"{self.settings.syncthing_local_dir}/{file}"

                # Abort if the file do not exist
                if not os.path.exists(local_path):
                    harmonize.log("file not exists", local_path)
                    return

                hash = hash_file(local_path)

                if action == "deleted":
                    harmonize.log("Syncthing: Remote image was deleted")
                    payload = {"hash": hash, "path": file}
                    self.queue.put(Types.IMMICH_DELETE_IMAGE, payload)

                elif action == "modified":
                    harmonize.log(
                        "Syncthing: New/changed image detected. Added to upload queue."
                    )
                    payload = {"hash": hash, "path": file}
                    self.queue.put(Types.IMMICH_NEW_IMAGE, payload)

            # Example: image deleted locally
            elif event["type"] == "LocalChangeDetected":
                harmonize.log("local file change: not implemented")
