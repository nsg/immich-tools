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

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    response = RedirectResponse(url='/docs')
    return response

@app.get("/users")
def get_users():
    users = db.list_users()
    return { x['id'] for x in users }

@app.get("/asset/checksum/{checksum}")
def get_asset_checksum(checksum: str):
    if len(checksum) % 2 == 0:
        assets = db.get_asset_checksum(checksum)
        if assets:
            return { "assets": x for x in assets }
    return { "assets": {} }
