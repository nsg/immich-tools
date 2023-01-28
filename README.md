# Immich Tools

**WORK IN PROGRESS**

Various tools that I use together with my [Immich](https://immich.app) installation to enhance it (from my point of view). I hope you find this useful to use as-is or as a starting point of some tweaks of your own. I'm happy to merge changes that do not alter the scope of this project to much.

## Micro Services

The tools are split in to different micro services. They are intended to be run as part of the Immich `docker-compose.yml` and reads it's configuration from Immich environment.

### API

Immich Tools API is an unofficial API that implements a few extra
utility API endpoints that Immich Server do not provide. These are
are used by the other services in Immich Tools to do various things.

Add this to `docker-compose.yml` launch the service, it will read it's configuration from `.env` like Immich. This service connects directly to the database.

```
  immich-tools-services-api:
    image: ghcr.io/nsg/immich-tools-services-api:master
    env_file:
      - .env
    restart: always
```

* `/users` - List User UUID:s
* `/asset/checksum/{checksum}` - Find asset by checksum, list Asset UUID
* `/asset/deleted/{minutes}` - List checksums of deleted files in the last {minutes}

**Warning** this service will alter the database. A table called `assets_delete_audits` will be created, together with a function called `log_assets_delete_audits()` and a trigger called `trigger_assets_delete_audits`.

### Syncthing

This connects to a Syncthing server and listens for file changes in a specified folder. This service also require read only access to the files to it can enhance the events with file hashes.

```
  immich-tools-services-syncthing:
    image: ghcr.io/nsg/immich-tools-services-syncthing:master
    environment:
      SYNCTHING_REST_URL: http://10.0.0.100:8384/rest
      SYNCTHING_FOLDER_ID: abcdef-ghi12
      SYNCTHING_API_KEY: aBcDefgHi6Jkl93GhiJKLmn8
      SYNCTHING_LOCAL_DIR: /syncthing
      IMMICH_EMAIL: user@example.com
      IMMICH_PASSWORD: myNicePassword
      IMMICH_TOOLS_API: immich-tools-services-api:8000
    env_file:
      - .env
    volumes:
      /mnt/syncthing:/syncthing
    restart: always
```

You need to have File Versioning turned on, set it to `Trash Can File Versioning`. To save some disk space, I recommend that you change `Clean out after` to a few days. This script assumes we use `.stversions`.

### Hasher

```
  immich-tools-services-api:
    image: ghcr.io/nsg/immich-tools-services-api:master
    env_file:
      - .env
    environment:
      SCAN_PATH: /scan
      SCAN_INTERVAL: 60
    volumes:
      /mnt/files:/scan
    restart: always
```
