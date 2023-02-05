### Harmonize

This harmonize (sync) a Synthing server with an Immich user. This is the core component that provides synchronization between these two services.

### Requirements

This connects to a Syncthing server and listens for file changes in a specified folder. This service also require read only access to the files to it can enhance the events with file hashes.

```yaml
  immich-tools-services-syncthing:
    image: ghcr.io/nsg/immich-tools-services-syncthing:master
    environment:
      SYNCTHING_REST_URL: http://10.0.0.100:8384/rest
      SYNCTHING_FOLDER_ID: abcdef-ghi12
      SYNCTHING_API_KEY: aBcDefgHi6Jkl93GhiJKLmn8
      SYNCTHING_LOCAL_DIR: /syncthing
      IMMICH_EMAIL: user@example.com
      IMMICH_PASSWORD: myNicePassword
      IMMICH_TOOLS_API: http://immich-tools-services-api:8000
      IMMICH_IMPORT_API: http://immich-tools-services-import:8001
    env_file:
      - .env
    volumes:
      - /phone/camera:/syncthing
    depends_on:
      - immich-server
    restart: always
```

You need to have File Versioning turned on, set it to `Trash Can File Versioning`. To save some disk space, I recommend that you change `Clean out after` to a few days. This script assumes we use `.stversions`.


    volumes:
      - /mnt/user_a:/user/5cd45f80-8b6c-4a01-9a81-72a89082e744
      - /mnt/user_b:/user/238776bb-5b0c-4fe4-98b1-cea72be79a28
