# Real World Example

## Prepare installation

Let's start with [Syncthing](https://syncthing.net/), install it on the same server as Immich. You need access to the shared folder.

* https://syncthing.net/downloads/

Immich runs in a `docker-compose.yml` file, and Syncthing also has a Docker image. The easiest way to get started is probably to run Syncthing inside that. See [the documentation](https://github.com/syncthing/syncthing/blob/main/README-Docker.md) how to configure it.

```yaml
  syncthing:
    image: syncthing/syncthing
    container_name: syncthing
    hostname: immich-syncthing
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - /mnt/syncthing:/var/syncthing
    ports:
      - 8384:8384       # Web UI
      - 22000:22000/tcp # TCP file transfers
      - 22000:22000/udp # QUIC file transfers
      - 21027:21027/udp # Receive local discovery broadcasts
    restart: unless-stopped
```

Configure Syncthing whoever you like, for this point on forward I will assume that you have two Immich users (`User A` and `User B`), each with it's own phone (`Phone A` and `Phone B`) syncing to different folders `/mnt/syncthing/phone_a` and `/mnt/syncthing/phone_b`. You have enabled `Trash Can File Versioning` on both folders.

## Immich Tools

You need one instance of the API server, this is not user specific so you never need more than one of these services.

```yaml
  immich-tools-services-api:
    image: ghcr.io/nsg/immich-tools-services-api:master
    env_file:
      - .env
    depends_on:
      - database
    restart: always
```

You need to deploy one instance of hasher for each folder. It's important that `SCAN_PATH` is unique to this user and folder.

```yaml

  immich-tools-services-hasher-phone-a:
    image: ghcr.io/nsg/immich-tools-services-hasher:master
    env_file:
      - .env
    environment:
      SCAN_PATH: /phone_a
      SCAN_INTERVAL: 60
    volumes:
      - /mnt/syncthing/phone_a:/phone_a
    depends_on:
      - database
    restart: always

  immich-tools-services-hasher-phone-b:
    image: ghcr.io/nsg/immich-tools-services-hasher:master
    env_file:
      - .env
    environment:
      SCAN_PATH: /phone_b
      SCAN_INTERVAL: 60
    volumes:
      - /mnt/syncthing/phone_b:/phone_b
    depends_on:
      - database
    restart: always    
```

You need one import service for each user

```yaml
  immich-tools-services-import-phone-a:
    image: ghcr.io/nsg/immich-tools-services-import:master
    env_file:
      - .env
    environment:
      IMMICH_KEY: api-key-for-user-a
    volumes:
      - /mnt/syncthing/phone_a:/import
    restart: always

  immich-tools-services-import-phone-b:
    image: ghcr.io/nsg/immich-tools-services-import:master
    env_file:
      - .env
    environment:
      IMMICH_KEY: api-key-for-user-b
    volumes:
      - /mnt/syncthing/phone_b:/import
    restart: always
```

... and finally 

```yaml
  immich-tools-services-syncthing-phone-a:
    image: ghcr.io/nsg/immich-tools-services-syncthing:master
    environment:
      SYNCTHING_REST_URL: http://10.0.0.100:8384/rest
      SYNCTHING_FOLDER_ID: abcdef-ghi12
      SYNCTHING_API_KEY: aBcDefgHi6Jkl93GhiJKLmn8
      SYNCTHING_LOCAL_DIR: /syncthing
      IMMICH_EMAIL: user_a@example.com
      IMMICH_PASSWORD: myNicePassword
      IMMICH_TOOLS_API: http://immich-tools-services-api:8000
      IMMICH_IMPORT_API: http://immich-tools-services-import-phone-a:8001
    env_file:
      - .env
    volumes:
      - /mnt/syncthing/phone_a:/syncthing
    depends_on:
      - immich-server
    restart: always

  immich-tools-services-syncthing-phone-b:
    image: ghcr.io/nsg/immich-tools-services-syncthing:master
    environment:
      SYNCTHING_REST_URL: http://10.0.0.100:8384/rest
      SYNCTHING_FOLDER_ID: abcdef-ghi13
      SYNCTHING_API_KEY: aBcDefgHi6Jkl93GhiJKLmn8
      SYNCTHING_LOCAL_DIR: /syncthing
      IMMICH_EMAIL: user_b@example.com
      IMMICH_PASSWORD: myNicePassword
      IMMICH_TOOLS_API: http://immich-tools-services-api:8000
      IMMICH_IMPORT_API: http://immich-tools-services-import-phone-b:8001
    env_file:
      - .env
    volumes:
      - /mnt/syncthing/phone_b:/syncthing
    depends_on:
      - immich-server
    restart: always
```
