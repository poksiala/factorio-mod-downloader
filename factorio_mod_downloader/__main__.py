import logging
import os
from typing import Optional

import requests

from .dependencies import solve_dependencies
from .download import download_mods
from .models import Auth


def fetch_token(client: requests.Session, username: str, token: str) -> str:
    url = "https://auth.factorio.com/api-login"
    login_data = dict(username=username, password=token, require_game_ownership=True)
    response = client.post(url, data=login_data)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list) and len(body) == 1
    return body[0]


def get_auth(client: requests.Session) -> Optional[Auth]:
    username = os.environ.get("FACTORIO_USERNAME")
    if username is None:
        return None
    token = os.environ.get("FACTORIO_TOKEN")
    password = os.environ.get("FACTORIO_PASSWORD")
    if token is None and password is not None:
        token = fetch_token(client, username, password)
    if token is None:
        return None
    return Auth(username=username, token=token)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.INFO)
    client = requests.Session()
    auth = get_auth(client)
    if auth is None:
        logging.error(
            "FACTORIO_USERNAME and FACTORIO_TOKEN or FACTORIO_PASSWORD must be defined."
        )
        exit(1)
    with open("modlist", "r") as f:
        mods = solve_dependencies(f.readlines(), client)
    logging.info("Resolved %d mods", len(mods))
    download_mods(mods, client, auth)
