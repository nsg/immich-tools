import requests

class ToolsApi:

    immich_tools_api: str

    def __init__(self, immich_tools_api) -> None:
        self.immich_tools_api = immich_tools_api

    def get_assets_by_hash(self, hash):
        r = requests.get(f"{self.immich_tools_api}/asset/checksum/{hash}")
        return r.json()['assets']

    def get_local_by_hash(self, hash):
        r = requests.get(f"{self.immich_tools_api}/local/checksum/{hash}")
        return r.json()['assets']

    def get_deleted_assets_last_n_minutes(self, minutes):
        r = requests.get(f"{self.immich_tools_api}/asset/deleted/{minutes}")
        return r.json()

class ImportApi:

    immich_import_api: str

    def __init__(self, immich_import_api) -> None:
        self.immich_import_api = immich_import_api

    def upload_image(self, path):
        r = requests.get(f"{self.immich_import_api}/import/{path}")
        if r.status_code != 200:
            print(f"Failed to import {path}", flush=True)
