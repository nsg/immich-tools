### Import

A simple API that wraps around [Immich CLI](https://github.com/immich-app/CLI) to upload images. I picked this solution due the fast moving nature of Immich and it's easier for me to keep up to date with the development. File uploads requires me to add a lot of metadata to the requests which is (at the moment) not documented.

I packages this as a separate micro service to keep it simple to maintain. This image is based **on top** of the official Immich CLI image, theoretically is should be possible to for me to just rebuild this image to get the latest upstream changes.

```yaml
  immich-tools-services-import:
    image: ghcr.io/nsg/immich-tools-services-import:master
    env_file:
      - .env
    volumes:
      - /mnt/user_a:/user/5cd45f80-8b6c-4a01-9a81-72a89082e744
      - /mnt/user_b:/user/238776bb-5b0c-4fe4-98b1-cea72be79a28
    restart: always

```

Each user in Immich has a User ID (represented by a UUID). You can see your ID from user settings page in Immich Web. Alternatively use Immich Tools API:s endpoint `/users`.

Mount the path and/or volume where a users syncthing files are stored (`/mnt/user_a` in this example) to the path `/user/<uuid>` inside the container. The foldername need to match an existing user.

| Path                             | Query      | Comment  |
| -------------------------------- | ---------- | -------- |
| `/import/{user_id}/{path}`       | immich_key | This will import the specified asset to Immich via the Immich CLI |

This will **write** links in a folder called `.link-import` inside each volume. The links will be removed but the folder will be left there. It's safe to remove it. This is due a limitation in the CLI, I hope I will be able to contribute a fix for this at a later date.
