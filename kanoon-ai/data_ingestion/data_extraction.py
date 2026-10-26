import json
import sys
from pathlib import Path
from typing import Dict, List
import httpx
from mistralai.client import Mistral
from config import ACTS, DOWNLOAD_TIMEOUT, MISTRAL_API_KEY, OCR_DIR, OCR_MODEL, OCR_TIMEOUT_MS, RAW_DIR
from logger import custom_logger

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

def mistral_ocr(pdf_path: Path) -> List[Dict]:
    """OCR a PDF with Mistral: upload it, OCR it through a signed URL, delete the upload. Running headers and footers come back separately, so they stay out of the page markdown."""
    mistral = Mistral(api_key=MISTRAL_API_KEY)
    uploaded = mistral.files.upload(file={"file_name": pdf_path.name, "content": pdf_path.read_bytes()}, purpose="ocr")
    try:
        signed = mistral.files.get_signed_url(file_id=uploaded.id, expiry=1)
        response = mistral.ocr.process(model=OCR_MODEL, document={"type": "document_url", "document_url": signed.url},extract_header=True, extract_footer=True, timeout_ms=OCR_TIMEOUT_MS)
    finally:
        mistral.files.delete(file_id=uploaded.id)
    return [{"page": p.index + 1, "markdown": p.markdown or ""} for p in response.pages]


def extract(act_id: str) -> List[Dict]:
    """The Act's pages as markdown, cached in data/ocr/<act>.json so we pay for OCR once."""
    path = OCR_DIR / f"{act_id}.json"
    if path.exists():
        return json.loads(path.read_text())
    if not MISTRAL_API_KEY:
        raise RuntimeError("Set MISTRAL_API_KEY in data_ingestion/.env")
    pages = mistral_ocr(download(act_id))
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pages, indent=1, ensure_ascii=False))
    custom_logger.info(f"extract | {act_id}: {len(pages)} pages, {sum(len(p['markdown']) for p in pages):,} chars")
    return pages


if __name__ == "__main__":
    for act_id in sys.argv[1:] or ACTS:
        extract(act_id)