import os
import time

import harmonize
from harmonize import HarmonizeQueue
from syncthing import SynthingThread
from immich import ImmichThread

harmonize.log("Harmonize initializing")
harmonize.log("Read and validate configuration from environment")

settings = harmonize.Settings()

settings.immich(
    os.getenv("IMMICH_SERVER_URL"),
    os.getenv("IMMICH_API_KEY"),
)

settings.syncthing(
    os.getenv("SYNCTHING_REST_URL"),
    os.getenv("SYNCTHING_API_KEY"),
    os.getenv("SYNCTHING_LOCAL_DIR"),
    os.getenv("SYNCTHING_FOLDER_ID"),
)

settings.immich_tools(
    os.getenv("IMMICH_TOOLS_API")
)

settings.immich_import(
    os.getenv("IMMICH_IMPORT_API")
)

harmonize.log("Starting background threads")

queue = HarmonizeQueue()

syncthing_thread = SynthingThread(settings, queue)
syncthing_thread.start()

immich_thread = ImmichThread(settings, queue)
immich_thread.start()

while True:
    if not queue.all_empty():
        harmonize.log(queue)
    time.sleep(1)
