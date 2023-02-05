import os
import sys
import time
import hashlib
import glob
import pathlib

from database import ImmichDatabase

DATABASE = os.getenv("DB_DATABASE_NAME", "immich")
HOST = os.getenv("DB_HOSTNAME", "127.0.0.1")
USERNAME = os.getenv("DB_USERNAME", "postgres")
PASSWORD = os.getenv("DB_PASSWORD", "postgres")
PORT = os.getenv("DB_PORT", 5432)

SCAN_PATH = os.getenv("SCAN_PATH", "/user")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "1"))
SCAN_FILEAGE = int(os.getenv("SCAN_FILEAGE", SCAN_INTERVAL * 2))

if not os.path.exists(SCAN_PATH):
    print(f"Scan folder {SCAN_PATH} not found", flush=True)
    sys.exit(1)

db = ImmichDatabase(DATABASE, HOST, USERNAME, PASSWORD, PORT)
db.provision_database()

user_path_ids = glob.glob(SCAN_PATH + "/*", recursive=True)


def hash_file(path):
    file_hash = hashlib.sha1()
    with open(path, "rb") as f:
        fb = f.read(2048)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(2048)
    return file_hash.hexdigest()


while True:
    for user_path_id in user_path_ids:
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
                db.set_asset_checksum(hash, user_id, user_path)
                print(hash, user_id, user_path, mtime, flush=True)
                clean_up = db.get_old_hashes(hash, user_id, user_path)
                for id in clean_up:
                    print("Remove old hash ", id, flush=True)
                    db.delete_asset_by_id(id)

    time.sleep(SCAN_INTERVAL)
