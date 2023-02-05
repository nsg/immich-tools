import os
import sys
import time
import hashlib
import glob
import pathlib
import threading
import re

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse

from database import ImmichDatabase

DATABASE = os.getenv("DB_DATABASE_NAME", "immich")
HOST = os.getenv("DB_HOSTNAME", "127.0.0.1")
USERNAME = os.getenv("DB_USERNAME", "postgres")
PASSWORD = os.getenv("DB_PASSWORD", "postgres")
PORT = os.getenv("DB_PORT", 5432)

SCAN_PATH = os.getenv("SCAN_PATH", "/user")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "60"))
SCAN_FILEAGE = int(os.getenv("SCAN_FILEAGE", SCAN_INTERVAL * 2))

if not os.path.exists(SCAN_PATH):
    print(f"Scan folder {SCAN_PATH} not found", flush=True)
    sys.exit(1)

def hash_file(path):
    file_hash = hashlib.sha1()
    with open(path, "rb") as f:
        fb = f.read(2048)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(2048)
    return file_hash.hexdigest()

class JumbleHasher(threading.Thread):

    user_path_ids: list
    db: ImmichDatabase

    def __init__(self) -> None:
        super().__init__()
        self.user_path_ids = glob.glob(SCAN_PATH + "/*", recursive=True)
        self.db = ImmichDatabase(DATABASE, HOST, USERNAME, PASSWORD, PORT)
        self.db.provision_database()

    def run(self, *args, **kwargs):
        print("Start Jumble Hasher Service", flush=True)

        while True:
            for user_path_id in self.user_path_ids:
                now = time.time()
                files = glob.glob(user_path_id + "/**", recursive=True)

                for f in files:
                    if os.path.isdir(f):
                        continue

                    pl = pathlib.Path(f)
                    user_id = pl.parts[2]
                    user_path = "/".join(pl.parts[3:])

                    mtime = os.path.getmtime(f)
                    if mtime > now - SCAN_FILEAGE:
                        hash = hash_file(f)
                        self.db.set_asset_checksum(hash, user_id, user_path)
                        print(hash, user_id, user_path, mtime, flush=True)
                        clean_up = self.db.get_old_hashes(hash, user_id, user_path)
                        for id in clean_up:
                            print("Remove old hash ", id, flush=True)
                            self.db.delete_asset_by_id(id)

            time.sleep(SCAN_INTERVAL)

hasher_thread = JumbleHasher()
hasher_thread.start()

app = FastAPI(
    title="Immich Tools Jumble",
    description="""
        Immich Tools Jumble
    """.strip(),
    version="0.1.0",
)

db = ImmichDatabase(DATABASE, HOST, USERNAME, PASSWORD, PORT)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    response = RedirectResponse(url="/docs")
    return response

@app.get("/user/{user_id}/{hash}")
def get_local_user_asset(user_id: str, hash: str):
    r = db.local_file(hash, user_id)
    return r

@app.delete("/user/{user_id}/{hash}")
def delete_local_user_asset(user_id: str, hash: str):
    r = db.local_file(hash, user_id)

    if not re.match("^[a-z0-9-]+$", user_id):
        message = {
            "message": "Malformed user_id"
        }
        return JSONResponse(content=message, status_code=401)

    if r['count'] > 1:
        message = {
            "message": "We found more than one match, abort!",
            "response": r
        }
        return JSONResponse(content=message, status_code=401)
    elif r['count'] == 0:
        message = {
            "message": "Hash not found in the database"
        }
        return JSONResponse(content=message, status_code=404)

    path = f"/user/{user_id}/{r['assets'][0]['path']}"

    if not os.path.exists(path):
        message = {
            "message": f"File not found: {path}"
        }
        return JSONResponse(content=message, status_code=404)

    os.unlink(path)

    return {"message": f"File {path} removed"}
