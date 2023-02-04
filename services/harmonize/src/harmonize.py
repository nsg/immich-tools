import os
import textwrap
from datetime import datetime
from queue import Queue


class HarmonizeException(Exception):
    pass


def fail(text_message):
    raise HarmonizeException(text_message)


def log(text_message):
    prefix = datetime.now().strftime("%H:%M:%S")
    message(f"[{prefix}] {text_message}")


def message(text_message):
    print(text_message, flush=True)


def banner(text_message, subtext=None):
    header_message = text_message.upper().ljust(65)

    message("\n+---                                                             ---+")
    message(f"| {header_message} |")
    if subtext:
        message(f"|{''.ljust(66)} |")
        for text in textwrap.wrap(subtext, width=65):
            message(f"| {text.ljust(65)} |")
    message("+---                                                             ---+\n")


class Settings:

    immich_url: str
    immich_apikey: str

    syncthing_url: str
    syncthing_apikey: str
    syncthing_local_dir: str
    syncthing_folder_id: str

    immich_tools_api: str
    immich_import_api: str

    program_start_ts: float

    def __init__(self) -> None:
        self.program_start_ts = datetime.utcnow().timestamp()

    def immich(self, url, apikey):
        self.immich_url = url
        self.immich_apikey = apikey

    def syncthing(self, url, apikey, local_path, folder_id):
        self.syncthing_url = url
        self.syncthing_apikey = apikey
        self.syncthing_local_dir = local_path
        self.syncthing_folder_id = folder_id

    def immich_tools(self, immich_tools_api):
        self.immich_tools_api = immich_tools_api

    def immich_import(self, immich_import_api):
        self.immich_import_api = immich_import_api

    def __str__(self) -> str:
        return str(
            {
                "immich": {
                    "url": self.immich_url,
                    "apikey": self.immich_apikey,
                },
                "syncthing": {
                    "url": self.syncthing_url,
                    "apikey": self.syncthing_apikey,
                    "local_dir": self.syncthing_local_dir,
                    "folder_id": self.syncthing_folder_id,
                },
            }
        )


class HarmonizeQueue(Queue):
    def message(self, message_type: int, message: object):
        self.put(HarmonizeMessage(message_type, message))


class HarmonizeMessage:

    message_type: str
    message_payload: object

    def __init__(self, message_type: int, message_payload: object) -> None:
        self.message_type = message_type
        self.message_payload = message_payload

    def __str__(self) -> str:
        return str(
            {"message_type": self.message_type, "message_payload": self.message_payload}
        )


class Types:

    IMMICH_NEW_IMAGE = 1
    IMMICH_DELETE_IMAGE = 2
