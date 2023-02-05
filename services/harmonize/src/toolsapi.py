import requests

import harmonize

class ToolsApi:

    immich_tools_api: str

    def __init__(self, settings: harmonize.Settings) -> None:
        self.immich_tools_api = settings.immich_tools_api

    def get_assets_by_hash(self, hash):
        r = requests.get(f"{self.immich_tools_api}/asset/checksum/{hash}")
        return r.json()["assets"]

    def get_local_by_hash(self, hash):
        r = requests.get(f"{self.immich_tools_api}/local/checksum/{hash}")
        return r.json()["assets"]

    def get_last_deleted_assets(self):
        r = requests.get(f"{self.immich_tools_api}/asset/deleted_audits")
        return r.json()


class ImportApi:

    immich_import_api: str
    immich_api_key: str

    def __init__(self, settings: harmonize.Settings) -> None:
        self.immich_import_api = settings.immich_import_api
        self.immich_api_key = settings.immich_apikey

    def upload_image(self, user_id, path):
        r = requests.get(f"{self.immich_import_api}/import/{user_id}/{path}?immich_key={self.immich_api_key}")
        if r.status_code != 200:
            print(f"Failed to import {path}", flush=True)


class JumbleApi:

    immich_jumble_api: str

    def __init__(self, settings: harmonize.Settings) -> None:
        self.immich_jumble_api = settings.immich_jumble_api

    def delete_image(self, user_id, hash):
        r = requests.delete(f"{self.immich_jumble_api}/user/{user_id}/{hash}")
        if r.status_code != 200:
            print(f"Failed to delete {hash} as user {user_id}", flush=True)
