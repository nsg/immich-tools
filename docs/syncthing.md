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
      IMMICH_IMPORT_API: immich-tools-services-import:8001
    env_file:
      - .env
    volumes:
      - /mnt/syncthing:/syncthing
    restart: always
```

You need to have File Versioning turned on, set it to `Trash Can File Versioning`. To save some disk space, I recommend that you change `Clean out after` to a few days. This script assumes we use `.stversions`.
