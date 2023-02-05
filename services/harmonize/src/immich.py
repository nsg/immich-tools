import threading
import json
import time

import requests

import harmonize
from harmonize import Types
from toolsapi import ToolsApi, ImportApi


class ImmichAPI:

    settings: harmonize.Settings
    headers: dict

    def __init__(self, settings: harmonize.Settings) -> None:
        self.settings = settings
        self.headers = {}
        self.headers["x-api-key"] = settings.immich_apikey
        self.headers["Content-Type"] = "application/json"
        self.headers["Accept"] = "application/json"

    def get_asset_by_id(self, asset_id):
        url = f"{self.settings.immich_url}/asset/assetById/{asset_id}"
        return self._request_get(url)

    def user_info(self):
        url = f"{self.settings.immich_url}/user/me"
        return self._request_get(url)

    def delete_assets(self, asset_ids):
        q = {"ids": asset_ids}
        url = f"{self.settings.immich_url}/asset"
        return self._request_delete(url, q)

    def _request_get(self, url) -> json:
        r = requests.get(url, headers=self.headers)
        if r.status_code not in [200, 201]:
            raise Exception(r.status_code, r.content)
        return json.loads(r.content)

    def _request_post(self, url, data) -> json:
        r = requests.post(url, data, headers=self.headers)
        if r.status_code not in [200, 201]:
            raise Exception(r.status_code, r.content)
        return json.loads(r.content)

    def _request_delete(self, url, data) -> json:
        r = requests.delete(url, data=json.dumps(data), headers=self.headers)
        if r.status_code not in [200, 201]:
            raise Exception(r.status_code, r.content)
        return json.loads(r.content)


class ImmichThread(threading.Thread):

    __settings: harmonize.Settings
    __queue: harmonize.HarmonizeQueue
    __immich: ImmichAPI
    __tools: ToolsApi
    __import: ImportApi

    def __init__(self, settings: harmonize.Settings, queue: harmonize.HarmonizeQueue) -> None:
        super().__init__()
        self.__settings = settings
        self.__queue = queue
        self.__immich = ImmichAPI(settings)
        self.__tools = ToolsApi(settings)
        self.__import = ImportApi(settings)

    def run(self, *args, **kwargs):
        harmonize.log("Immich thread started")

        while True:
            if not self.__queue.empty(Types.IMMICH_NEW_IMAGE):
                item = self.__queue.get(Types.IMMICH_NEW_IMAGE)
                #file_hash = item["hash"]
                file_path = item["path"]
                self.__import.upload_image(file_path)
                harmonize.log("Add new image")

            if not self.__queue.empty(Types.IMMICH_DELETE_IMAGE):
                item = self.__queue.get(Types.IMMICH_DELETE_IMAGE)
                file_hash = item["hash"]
                assets = self.__tools.get_assets_by_hash(file_hash)

                if len(assets) > 1:
                    harmonize.fail(
                        f"Got {len(assets)} results for {file_hash}, abort!"
                    )

                if len(assets) == 0:
                    harmonize.log(
                        f"Found no remote files for hash {file_hash}, nothing will be removed from Immich"
                    )

                immich_image = self.__immich.get_asset_by_id(assets[0])
                immich_id = self.__immich.user_info()['id']

                if immich_image['ownerId'] != immich_id:
                    harmonize.fail("Error, image now owned by the expected account")

                self.__immich.delete_assets([assets[0]])

            time.sleep(5)
