import os
import subprocess
import pathlib
import time

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Immich Tools Import Service",
    description="""
    """.strip(),
    version="0.1.0"
)

IMMICH_SERVER_URL = os.getenv("IMMICH_SERVER_URL")
IMMICH_KEY = os.getenv("IMMICH_KEY")

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    response = RedirectResponse(url='/docs')
    return response

@app.get("/import/{path}")
def import_path(path: str):
    base_path = "/import"
    path_import = f"/import/{path}"
    filename = pathlib.Path(path_import).name
    link_import_path = f"{base_path}/.link-import"
    temp_link_name = f"{link_import_path}/{filename}"

    if not os.path.exists(link_import_path):
        os.mkdir(link_import_path)

    os.link(path_import, temp_link_name)   

    command = [
        "/usr/local/bin/immich",
        "upload",
        "--yes",
        "--key", IMMICH_KEY,
        "--server", f"{IMMICH_SERVER_URL}/api",
        "-d", link_import_path
    ]
    subprocess.run(" ".join(command), shell=True)
    os.remove(temp_link_name)

    print(f"Imported {path_import} to Immich", flush=True)
