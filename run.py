#!/usr/bin/env python3

import time
import os

from immich.api import ImmichAPI
from syncthing.api import SyncthingAPI

from settings import SETTINGS

im = ImmichAPI(SETTINGS['IMMICH_API_URL'])
im.login(SETTINGS['IMMICH_USERNAME'], SETTINGS['IMMICH_PASSWORD'])

sy = SyncthingAPI(SETTINGS['SYNCTHING_API_URL'], SETTINGS['SYNCTHING_API_KEY'])

SYNCTHING_IDENT = SETTINGS['SYNCTHING_IDENT']

def log(s):
    print(s, flush=True)

def remove_from_immich(path):
    file_name = os.path.splitext(path)[0]
    im_asset = im.search_asset(file_name)
    if im_asset:
        if len(im_asset) > 1:
            log(f"Error, multiple matches for {file_name}")
            return False

        resp = im.delete_asset([im_asset[0]['id']])

        if len(resp) > 1 or resp[0]['status'] != "SUCCESS":
            log("Error, incorrect delete:")
            log(resp)
            return False
    else:
        log(f"Asset {path} not found in Immich")
        return False

    log(f"Remove asset {resp[0]['id']} from Immich (search: {path})")
    return True

last_seen_id = None
while True:

    # Ask for new events
    for event in sy.get_events_disk(since=last_seen_id):

        # Only care for remote changes
        if event.get("type") == "RemoteChangeDetected":

            # Only care for file delete events with a correct ident
            if (
                event["data"]["action"] == "deleted"
                and event["data"]["type"] == "file"
                and event["data"]["modifiedBy"] == SYNCTHING_IDENT
            ):
                remove_from_immich(event["data"]["path"])

    last_seen_id = event.get("id")
    time.sleep(5)
