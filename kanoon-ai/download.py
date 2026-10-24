from pathlib import Path

import httpx

from config import DOWNLOAD_TIMEOUT, RAW_DIR
from logger import custom_logger
from sources import ACTS


def download(act_id: str) -> Path:
    """Fetch the Act's PDF into data/raw/ once. A PDF already there is reused."""
    act = ACTS[act_id]
    path = RAW_DIR / f"{act_id}.pdf"
    if path.exists():
        return path
    response = httpx.get(act["url"], timeout=DOWNLOAD_TIMEOUT, follow_redirects=True)
    if response.status_code != 200 or not response.content.startswith(b"%PDF"):
        raise RuntimeError(f"Couldn't download {act_id} (status {response.status_code}). "
                           f"Save it from {act['official']} as {path}")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    custom_logger.info(f"download | {act_id}: {len(response.content) // 1024} KB")
    return path
