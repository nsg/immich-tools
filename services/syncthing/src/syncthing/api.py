import requests

class SyncthingAPI:
    
    def __init__(self, server_rest_url, api_key) -> None:
        self.server_rest_url = server_rest_url
        self.api_key = api_key
        self.config = self.fetch_config()


    def get(self, url):
        return self.req(url).json()

    def put(self, url, data):
        return self.req(url, put=True, data=data)

    def req(self, url, put=False, data={}):

        headers = {
            "X-API-Key": self.api_key
        }

        if put:
            r = requests.put(f"{self.server_rest_url}/{url}", headers=headers, json=data)
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

    def fetch_config(self):
        return self.get("config")

    def push_config(self):
        return self.put("config", self.config)
