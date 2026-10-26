import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
OCR_MODEL = "mistral-ocr-latest"  # checked 2026-10-24: https://docs.mistral.ai/capabilities/document_ai/basic_ocr/
OCR_TIMEOUT_MS = 900_000

# Every step writes to its own folder, so each one can be re-run alone (git-ignored).
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"          # downloaded PDFs
OCR_DIR = DATA_DIR / "ocr"          # Mistral OCR pages (cached: OCR costs money)
CLEAN_DIR = DATA_DIR / "cleaned"    # cleaned pages
CHUNKS_DIR = DATA_DIR / "chunks"    # final chunks

# One entry per Act. `url` is where we download from, `official` is the page we cite,
# `as_of` is the date of the text we index.
ACTS = {
    "bns": {
        "title": "Bharatiya Nyaya Sanhita, 2023",
        "unit": "Section",
        # Gazette of India copy (Act No. 45 of 2023). India Code blocks scripted downloads.
        "url": "https://prsindia.org/files/bills_acts/bills_parliament/2023/The%20Bharatiya%20Nyaya%20Sanhita,%202023.pdf",
        "official": "https://www.indiacode.nic.in/handle/123456789/20062",
        "as_of": "2023-12-25",
    },
}

DOWNLOAD_TIMEOUT = 60

# Fixed-size chunking: every chunk is this many tokens, whatever the structure, with overlap.
TOKENIZER = "o200k_base"
CHUNK_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 100