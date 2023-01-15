import time

#from fastapi import BackgroundTasks, FastAPI
#from fastapi.responses import RedirectResponse

from syncthing.api import SyncthingAPI
from syncthing.config import SyncthingConfig

time.sleep(5)

sc = SyncthingConfig("/var/syncthing/config/config.xml")
api = SyncthingAPI("http://127.0.0.1:8384/rest", sc.apikey())

#app = FastAPI(
#    title="Immich Tools Syncthing",
#    description="""
#        TODO
#    """.strip(),
#    version="0.1.0"
#)

#@app.get("/", include_in_schema=False)
#def redirect_to_docs():
#    response = RedirectResponse(url='/docs')
#    return response

api.config['gui']['user'] = "foo"
api.config['gui']['password'] = "bar"

api.config['options']['urAccepted'] = -1
api.config['options']['urSeen'] = 3

api.config['folders'] = [
    {
        'id': 'default',
        'label': 'A paused folder',
        'filesystemType': 'basic',
        'path': '/var/syncthing/Sync',
        'type': 'sendreceive',
        'devices': [],
        'rescanIntervalS': 3600,
        'fsWatcherEnabled': True,
        'fsWatcherDelayS': 10,
        'ignorePerms': False,
        'autoNormalize': True,
        'minDiskFree': {
            'value': 1,
            'unit': '%'
        },
        'versioning': {
            'type': '',
            'params': {},
            'cleanupIntervalS': 3600,
            'fsPath': '',
            'fsType': 'basic'
        },
        'copiers': 0,
        'pullerMaxPendingKiB': 0,
        'hashers': 0,
        'order': 'random',
        'ignoreDelete': False,
        'scanProgressIntervalS': 0,
        'pullerPauseS': 0,
        'maxConflicts': 10,
        'disableSparseFiles': False,
        'disableTempIndexes': False,
        'paused': True,
        'weakHashThresholdPct': 25,
        'markerName': '.stfolder',
        'copyOwnershipFromParent': False,
        'modTimeWindowS': 0,
        'maxConcurrentWrites': 2,
        'disableFsync': False,
        'blockPullOrder': 'standard',
        'copyRangeMethod': 'standard',
        'caseSensitiveFS': False,
        'junctionsAsDirs': False,
        'syncOwnership': False,
        'sendOwnership': False,
        'syncXattrs': False,
        'sendXattrs': False,
        'xattrFilter': {
            'entries': [],
            'maxSingleEntrySize': 1024,
            'maxTotalSize': 4096
        }
    }
]

api.push_config()

time.sleep(2)

last_seen_id = None
while True:
    for event in api.get_events_disk(since=last_seen_id):
        print(event)
        last_seen_id = event.get("id")
        time.sleep(2)
