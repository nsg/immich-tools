import json

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from database import ImmichDatabase

app = FastAPI(
    title="Immich Tools API",
    description="""
        Immich Tools API is an unofficial API that implements a few extra
        utility API endpoints that Immich Server do not provide. These are
        are used by the other services in Immich Tools to do various things.
    """.strip(),
    version="0.1.0"
)

db = ImmichDatabase()
db.provision_delete_trigger()

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    response = RedirectResponse(url='/docs')
    return response

@app.get("/users")
def get_users():
    return db.list_users()

@app.get("/asset/checksum/{checksum}")
def get_asset_checksum(checksum: str):
    if len(checksum) % 2 == 0:
        return db.get_asset_checksum(checksum)
    return { "assets": [], "count": 0 }

@app.get("/asset/deleted")
def get_asset_deleted():
    return db.list_deleted_assets_last_n_minutes(5)
