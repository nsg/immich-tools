### Hasher

This service recursively scans a specified folder and maintains a lookup table for `(path, sha1hash)` pairs.

```yaml
  immich-tools-services-hasher:
    image: ghcr.io/nsg/immich-tools-services-hasher:master
    env_file:
      - .env
    environment:
      SCAN_PATH: /camera
      SCAN_INTERVAL: 60
    volumes:
      - /phone/camera:/camera
    depends_on:
      - database
    restart: always
```

**Warning** this service will alter the database. A table called `hasher_scanned_files` will be created.

For a full import of all data place a file called `.scan-all` in `SCAN_PATH` and wait for the next `SCAN_INTERVAL`. Remove the file to only import new files (modification time is used for this).
