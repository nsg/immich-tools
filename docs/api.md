### API

Immich Tools API is an unofficial API that implements a few extra
utility API endpoints that Immich Server do not provide. These are
are used by the other services in Immich Tools to do various things.

Add this to `docker-compose.yml` launch the service, it will read it's configuration from `.env` like Immich. This service connects directly to the database.

```yaml
  immich-tools-services-api:
    image: ghcr.io/nsg/immich-tools-services-api:master
    env_file:
      - .env
    depends_on:
      - database
    restart: always
```

| Path                             | Query   | Comment          |
| -------------------------------- | ------- | ---------------- |
| `/users`                         |         | List User UUID:s |
| `/asset/checksum/{checksum}`     | user_id | Find asset by checksum, optional filter by User ID |
| `/asset/deleted_audits`          |         | List checksums of files deleted in the last 2 minutes |
| `/local/checksum/{checksum}`     |         | Find local asset by checksum (indexed by the hasher service) |

**Warning** this service will alter the database. A table called `assets_delete_audits` will be created, together with a function called `log_assets_delete_audits()` and a trigger called `trigger_assets_delete_audits`.
