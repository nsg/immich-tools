import os
import sys
import time
import hashlib
import glob

from database import ImmichDatabase

DATABASE = os.getenv("DB_DATABASE_NAME", "immich")
HOST = os.getenv("DB_HOSTNAME", "127.0.0.1")
USERNAME = os.getenv("DB_USERNAME", "postgres")
PASSWORD = os.getenv("DB_PASSWORD", "postgres")
PORT = os.getenv("DB_PORT", 5432)

SCAN_PATH = os.getenv("SCAN_PATH", "/scan")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "1"))
SCAN_FILEAGE = int(os.getenv("SCAN_FILEAGE", SCAN_INTERVAL * 2))

if os.path.exists(SCAN_PATH):
    print(f"Scan folder is: {SCAN_PATH}")
else:
    print(f"Scan folder {SCAN_PATH} not found")
    sys.exit(1)

db = ImmichDatabase(DATABASE, HOST, USERNAME, PASSWORD, PORT)
db.provision_database()

def hash_file(path):
    file_hash = hashlib.sha1()
    with open(path, 'rb') as f:
        fb = f.read(2048)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(2048)
    return file_hash.hexdigest()

while True:
    if os.path.isfile(f"{SCAN_PATH}/.scan-all"):
        now = 0.0
        print(f".scan-all file found in {SCAN_PATH}, timestamp constraint will be ignored", flush=True)
    else:
        now = time.time()

    files = glob.glob(SCAN_PATH + '/**/*', recursive=True)
    for file in files:
        if os.path.isfile(file):
            mtime = os.path.getmtime(file)
            if mtime > now - SCAN_FILEAGE:
                hash = hash_file(file)
                db.set_asset_checksum(file, hash)
                print(hash, file, mtime, flush=True)
                clean_up = db.get_old_hashes(file, hash)
                for id in clean_up:
                    db.delete_asset_by_id(id)


    time.sleep(SCAN_INTERVAL)
