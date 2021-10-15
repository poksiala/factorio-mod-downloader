import hashlib
import logging
from typing import List

import requests
import tenacity
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed
from tenacity.after import after_log

from .models import Auth, DownloadDetails

logger = logging.getLogger(__name__)


def verify_download(mod: DownloadDetails, content: bytes):
    logger.debug("Verifying mod SHA1 sum")
    sha1 = hashlib.sha1()
    sha1.update(content)
    digest = sha1.hexdigest()
    assert digest == mod.sha1, "Downloaded file SHA1 does not match expected SHA1"


def download_mod_content(
    mod: DownloadDetails, client: requests.Session, auth: Auth
) -> bytes:
    url = f"{mod.download_url}?username={auth.username}&token={auth.token}"
    response = client.get(url, allow_redirects=True)
    return response.content


def write_content_on_disk(file_name: str, content: bytes):
    logger.debug("Writing file %s", file_name)
    with open(file_name, "wb") as output_file:
        output_file.write(content)


@tenacity.retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    after=after_log(logger, logging.WARNING),
)
def download_mod(mod: DownloadDetails, client: requests.Session, auth: Auth):
    logger.info("Downlaoding mod %s==%s", mod.name, mod.version)
    content = download_mod_content(mod, client, auth)
    verify_download(mod, content)
    write_content_on_disk(mod.file_name, content)


def download_mods(mods: List[DownloadDetails], client: requests.Session, auth: Auth):
    for mod in mods:
        download_mod(mod, client, auth)
