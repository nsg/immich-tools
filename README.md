# Immich Tools

WORK IN PROGRESS

Various tools that I use together with my [Immich](https://immich.app) installation to enhance it (from my point of view). I hope you find this useful to use as-is or as a starting point of some tweaks of your own. I'm happy to merge changes that do not alter the scope of this project to much.

## Micro Services

Micro services intended to be run as part of the Immich `docker-compose.yml` are located in `services/`.

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

### Syncthing


