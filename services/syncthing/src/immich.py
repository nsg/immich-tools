import requests
import json

class ImmichAPI:

    def __init__(self, server_api) -> None:
        self.accessToken = None
        self.userId = None
        self.userEmail = None
        self.firstName = None
        self.lastName = None
        self.isAdmin = None
        self.profileImagePath = None
        self.shouldChangePassword = None
        self.server_api = server_api

    def request_post(self, url, data, headers={}) -> json:
        if self.accessToken:
            headers["Authorization"] = f"Bearer {self.accessToken}"
        r = requests.post(url, data, headers=headers)
        if r.status_code not in [200, 201]:
            raise Exception(r.status_code, r.content)
        return json.loads(r.content)

    def request_delete(self, url, data, headers={}) -> json:
        if self.accessToken:
            headers["Authorization"] = f"Bearer {self.accessToken}"
        headers['Content-Type'] = "application/json"
        headers['Accept'] = "application/json"
        r = requests.delete(url, data=json.dumps(data), headers=headers)
        if r.status_code not in [200, 201]:
            raise Exception(r.status_code, r.content)
        return json.loads(r.content)

    def request_get(self, url, headers={}) -> json:
        if self.accessToken:
            headers["Authorization"] = f"Bearer {self.accessToken}"
        r = requests.get(url, headers=headers)
        if r.status_code not in [200, 201]:
            raise Exception(r.status_code, r.content)
        return json.loads(r.content)

    def login(self, email, password):
        r = self.request_post(f"{self.server_api}/auth/login", data={"email": email, "password": password})

        self.accessToken = r['accessToken']
        self.userId = r['userId']
        self.userEmail = r['userEmail']
        self.firstName = r['firstName']
        self.lastName = r['lastName']
        self.isAdmin = r['isAdmin']
        self.profileImagePath = r['profileImagePath']
        self.shouldChangePassword = r['shouldChangePassword']

    def get_all_users(self, all=True):
        q = "true" if all else "false"
        url = f"{self.server_api}/user?isAll={q}"
        return self.request_get(url)

    def get_my_user_info(self):
        url = f"{self.server_api}/user/me"
        return self.request_get(url)

    def get_asset_by_id(self, asset_id):
        url = f"{self.server_api}/asset/assetById/{asset_id}"
        return self.request_get(url)

    def search_asset(self, term):
        q = { "searchTerm": term }
        url = f"{self.server_api}/asset/search"
        return self.request_post(url, q)

    def delete_assets(self, asset_ids):
        q = { "ids": asset_ids }
        url = f"{self.server_api}/asset"
        return self.request_delete(url, q)
