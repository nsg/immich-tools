### Import

A simple API that wraps around [Immich CLI](https://github.com/immich-app/CLI) to upload images. I picked this solution due the fast moving nature of Immich and it would be a pain for me to keep up to date with the development. File uploads requires me to add a lot of metadata to the requests which is (at the moment) not documented.

I packages this as a separate micro service to keep it simple to maintain. This image is based **on top** of the official Immich CLI image, theoretically is should be possible to for me to just rebuild this image to get the latest upstream changes.

```
  immich-tools-services-import:
    image: ghcr.io/nsg/immich-tools-services-import:master
    env_file:
      - .env
    environment:
      IMMICH_KEY: aImmicHtOKenGENeraTedFromWebUIforAUser
    volumes:
      - /mnt/files:/import
    restart: always
```

API:

* `/import/{path}` this will import the specified asset to Immich via the Immich CLI

This will **write** links in a folder called `.link-import` inside `/import`. The links will be removed but the folder will be left there. It's safe to remove it. This is due a limitation in the CLI, I hope I will be able to contribute a fix for this at a later date.
