import time
import os
import sys
from datetime import datetime
import hashlib

from syncthing import SyncthingAPI
from immich import ImmichAPI
from toolsapi import ToolsApi, ImportApi

# Specified in docker-compose.yml
IMMICH_EMAIL = os.getenv("IMMICH_EMAIL")
IMMICH_PASSWORD = os.getenv("IMMICH_PASSWORD")
SYNCTHING_REST_URL = os.getenv("SYNCTHING_REST_URL")
SYNCTHING_API_KEY = os.getenv("SYNCTHING_API_KEY")
SYNCTHING_LOCAL_DIR = os.getenv("SYNCTHING_LOCAL_DIR")
SYNCTHING_FOLDER_ID = os.getenv("SYNCTHING_FOLDER_ID")
IMMICH_TOOLS_API = os.getenv("IMMICH_TOOLS_API")
IMMICH_IMPORT_API = os.getenv("IMMICH_IMPORT_API")

# Read from .env
IMMICH_SERVER_URL = os.getenv("IMMICH_SERVER_URL")

def parse_nanodate(s):
    s = s.split(".")[0]
    return datetime.strptime(f"{s}", "%Y-%m-%dT%H:%M:%S")

sy = SyncthingAPI(SYNCTHING_REST_URL, SYNCTHING_API_KEY)
sy_folders = [ x['id'] for x in sy.fetch_config()['folders'] ]

if SYNCTHING_FOLDER_ID in sy_folders:
    print(f"SYNCTHING: Found local folder folder {SYNCTHING_LOCAL_DIR}", flush=True)
else:
    print(f"SYNCTHING: Local directory {SYNCTHING_FOLDER_ID} not found in {sy_folders}", flush=True)
    sys.exit(1)

if os.path.exists(SYNCTHING_LOCAL_DIR):
    print(f"SYNCTHING: Local path to files {SYNCTHING_LOCAL_DIR}", flush=True)
else:
    print(f"SYNCTHING: Local path {SYNCTHING_LOCAL_DIR} not found", flush=True)
    sys.exit(1)

im = ImmichAPI(f"{IMMICH_SERVER_URL}")
im.login(IMMICH_EMAIL, IMMICH_PASSWORD)
user_info = im.get_my_user_info()
print(f"IMMICH:    Logged in as {user_info['email']}", flush=True)

print("SYNCTHING: Listen for events from Syncthing", flush=True)

to = ToolsApi(IMMICH_TOOLS_API)
ip = ImportApi(IMMICH_IMPORT_API)

def hash_file(path):
    file_hash = hashlib.sha1()
    with open(path, 'rb') as f:
        fb = f.read(2048)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(2048)
    return file_hash.hexdigest()


def tick(event):

    # Only listen on events from SYNCTHING_FOLDER_ID
    if event['data']['folder'] == SYNCTHING_FOLDER_ID:

        event_ts = parse_nanodate(event['time']).timestamp()
        action = event['data']['action']
        modby = event['data']['modifiedBy']
        file = event['data']['path']

        # Only process events in the future
        if event_ts < program_start_ts:
            return

        # Ignore non-files (like directories)
        if event['data']['type'] != "file":
            return

        # Ignore hidden images (for example trashed files)
        if file[0] == ".":
            return

        # Example: image created and/or deleted on the phone
        if event['type'] == "RemoteChangeDetected":

            # Set path to the local files
            if action == "deleted":
                local_path = f"{SYNCTHING_LOCAL_DIR}/.stversions/{file}"
            else:
                local_path = f"{SYNCTHING_LOCAL_DIR}/{file}"

            # Abort if the file do not exist
            if not os.path.exists(local_path):
                print("file not exists", local_path, flush=True)
                return

            hash = hash_file(local_path)
            assets = to.get_assets_by_hash(hash)

            if action == "deleted":

                # This should not happen, abort if we got several matches
                if len(assets) > 1:
                    print(f"Got {len(assets)} results for {hash}, abort!", flush=True)
                    return

                # Image not found in Immich, maybe it was never there? Or
                # maybe it was removed from Immich mobile app? There is
                # nothing to remove.
                if len(assets) == 0:
                    print(f"Found no remote files for hash {hash}, nothing will be removed from Immich", flush=True)
                    return

                immich_image = im.get_asset_by_id(assets[0])

                # Make sure that this is an image that we owns
                if immich_image['ownerId'] != im.get_my_user_info()['id']:
                    print("Error, image now owned by expected person", flush=True)
                    return

                im.delete_assets([assets[0]])

            elif action == "modified":
                ip.upload_image(file)

        # Example: image deleted locally
        elif event['type'] == "LocalChangeDetected":
            print("local file change: not implemented", flush=True)

def process_assets_delete_audits():
    remove_locals = to.get_last_deleted_assets()
    for remove_local in remove_locals:
        remove_file = to.get_local_by_hash(remove_local["checksum"])
        remove_path = remove_file["path"]
        if os.path.exists(remove_file):
            print(f"File removed from Immich Server, remote {remove_file}")
            os.remove(remove_file)
        else:
            print(f"File removed from Immich Server, file {remove_file} do not exists")

program_start_ts = datetime.utcnow().timestamp()
last_seen_id = None
while True:
    sec = datetime.now().second

    if sec % 10 == 0:
        for event in sy.get_events_disk(since=last_seen_id):
            tick(event)
        last_seen_id = event.get("id")

    if sec % 30 == 0:
        process_assets_delete_audits()

    time.sleep(1)
