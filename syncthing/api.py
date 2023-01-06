import requests

class SyncthingAPI:
    
    def __init__(self, server_rest_url, api_key) -> None:
        self.server_rest_url = server_rest_url
        self.api_key = api_key


    def get_events_disk(self, since=None):
        if since:
            url = f"{self.server_rest_url}/events/disk?since={since}"
        else:
            url = f"{self.server_rest_url}/events/disk"

        headers = {
            "X-API-Key": self.api_key
        }

        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            raise Exception(f"Syncthing API returned {r.status_code}. {r.content}")

        return r.json()
