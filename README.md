# sync-immich

Immich is an awesome Google Photos replacement, but the software is still early days and some features are missing. This repository contains various hacks and tweaks that I use to make it usable for me and my partner.

## Sync delete events from [Syncthing](https://syncthing.net/) to [Immich](https://immich.app)

* Subscribe for events of `RemoteChangeDetected` in Syncthing
* Filter on the identifier (the short form found in the GUI)
* Search in Immich for the filename
* If found, remove the image in Immich

This will break down if multiple files has the same filename, the script will only remove files if a single hit is found. My phone use long names like `PXL_20230106_210505099.jpg` so it's probably fine!

## Note

This is a hack that I use, only use this if you understand what this does. This can eat your files depending on your setup.
