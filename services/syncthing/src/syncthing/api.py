import requests
import re


def normalize(str):
    return re.sub(r"[^A-Za-z0-9]", "-", str)


def slug(str):
    return re.sub(r"[^a-z0-9]", "-", str.lower())


class SyncthingAPI:
    def __init__(self, server_rest_url, api_key) -> None:
        self.server_rest_url = server_rest_url
        self.api_key = api_key
        self.fetch_config()

    def get(self, url):
        return self.req(url).json()

    def put(self, url, data):
        return self.req(url, put=True, data=data)

    def req(self, url, put=False, data={}):

        headers = {"X-API-Key": self.api_key}

        if put:
            r = requests.put(
                f"{self.server_rest_url}/{url}", headers=headers, json=data
            )
        else:
            r = requests.get(f"{self.server_rest_url}/{url}", headers=headers)

        if r.status_code != 200:
            raise Exception(f"Syncthing API returned {r.status_code}. {r.content}")

        return r

    def get_events_disk(self, since=None):
        if since:
            url = f"events/disk?since={since}"
        else:
            url = f"events/disk"

        return self.get(url)

    def get_pending_folders(self):
        return self.get("cluster/pending/folders")

    def get_pending_devices(self):
        return self.get("cluster/pending/devices")

    def fetch_config(self):
        self.config = self.get("config")

    def save_config(self):
        return self.put("config", self.config)

    def get_myid(self):
        status = self.get("system/status")
        return status['myID']

    def set_userpass(self, username, password):
        self.config["gui"]["user"] = username
        self.config["gui"]["password"] = password

    def deny_statistics(self):
        self.config["options"]["urAccepted"] = -1
        self.config["options"]["urSeen"] = 3

    def add_folder(self, name, remote_device_id):
        self.config["folders"].append(
            {
                "id": f"{slug(name)}",
                "label": name,
                "filesystemType": "basic",
                "path": f"/var/syncthing/{normalize(name)}",
                "type": "sendreceive",
                "devices": [
                    {
                        "deviceID": self.get_myid(),
                        "introducedBy": "",
                        "encryptionPassword": "",
                    },
                    {
                        "deviceID": remote_device_id,
                        "introducedBy": "",
                        "encryptionPassword": "",
                    },
                ],
                "rescanIntervalS": 3600,
                "fsWatcherEnabled": True,
                "fsWatcherDelayS": 10,
                "ignorePerms": False,
                "autoNormalize": True,
                "minDiskFree": {"value": 128, "unit": "MB"},
                "versioning": {
                    "type": "trashcan",
                    "params": {"cleanoutDays": "7"},
                    "cleanupIntervalS": 3600,
                    "fsPath": "",
                    "fsType": "basic",
                },
                "copiers": 0,
                "pullerMaxPendingKiB": 0,
                "hashers": 0,
                "order": "random",
                "ignoreDelete": False,
                "scanProgressIntervalS": 0,
                "pullerPauseS": 0,
                "maxConflicts": 10,
                "disableSparseFiles": False,
                "disableTempIndexes": False,
                "paused": False,
                "weakHashThresholdPct": 25,
                "markerName": ".stfolder",
                "copyOwnershipFromParent": False,
                "modTimeWindowS": 0,
                "maxConcurrentWrites": 2,
                "disableFsync": False,
                "blockPullOrder": "standard",
                "copyRangeMethod": "standard",
                "caseSensitiveFS": False,
                "junctionsAsDirs": False,
                "syncOwnership": False,
                "sendOwnership": False,
                "syncXattrs": False,
                "sendXattrs": False,
                "xattrFilter": {
                    "entries": [],
                    "maxSingleEntrySize": 1024,
                    "maxTotalSize": 4096,
                },
            }
        )

    def remove_folder(self, name: str):
        folders = []
        for folder in self.config["folders"]:
            if folder["id"] != slug(name):
                folders.append(folder)
        self.config["folders"] = folders

    def folders(self, fetch: bool = False):
        if fetch:
            self.fetch_config()
        return self.config["folders"]

    def add_device(self, id: str, name: str):
        self.config["devices"].append(
            {
                "deviceID": id,
                "name": name,
                "addresses": ["dynamic"],
                "compression": "metadata",
                "certName": "",
                "introducer": False,
                "skipIntroductionRemovals": False,
                "introducedBy": "",
                "paused": False,
                "allowedNetworks": [],
                "autoAcceptFolders": False,
                "maxSendKbps": 0,
                "maxRecvKbps": 0,
                "ignoredFolders": [],
                "maxRequestKiB": 0,
                "untrusted": False,
                "remoteGUIPort": 0,
            }
        )

    def devices(self, fetch: bool = False):
        if fetch:
            self.fetch_config()
        return self.config["devices"]
