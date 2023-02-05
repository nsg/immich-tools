### Hasher

This service will build a lookup table for `(user_id, sha1hash)` pairs. Immich Tools uses the image sha1 hashes to identify images, Immich maintains hashes for all assets in the database (exposed by Immich Tools API). What's missing is hashes for files outside Immich like files in your Syncthing folders.

If an image is deleted in Immich Web the deleted images hash is saved so Harmonize can clean it up from the associated syncthing folder as well to keep the state synchronized. It would be slow to search the filesystem for a specific file by hash value each time, this service solves this by indexing and caches the hash in the database.

```yaml
  immich-tools-services-hasher:
    image: ghcr.io/nsg/immich-tools-services-hasher:master
    env_file:
      - .env
    volumes:
      - /mnt/user_a:/user/5cd45f80-8b6c-4a01-9a81-72a89082e744
      - /mnt/user_b:/user/238776bb-5b0c-4fe4-98b1-cea72be79a28
    depends_on:
      - database
    restart: always
```

**Warning** this service will alter the database. A table called `hasher_scanned_files` will be created.

Each user in Immich has a User ID (represented by a UUID). You can see your ID from user settings page in Immich Web. Alternatively use Immich Tools API:s endpoint `/users`.

Mount the path and/or volume where a users syncthing files are stored (`/mnt/user_a` in this example) to the path `/user/<uuid>` inside the container. The foldername need to match an existing user.

The program will index all folders mounted under `/user/*` inside the container.
