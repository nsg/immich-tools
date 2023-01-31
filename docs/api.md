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
* `/local/checksum/{checksum}` - Find local asset by checksum (indexed by the hasher service)

**Warning** this service will alter the database. A table called `assets_delete_audits` will be created, together with a function called `log_assets_delete_audits()` and a trigger called `trigger_assets_delete_audits`.
