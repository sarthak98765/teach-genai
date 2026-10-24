from pathlib import Path

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
PARSED_DIR = ROOT / "data" / "parsed"
CHUNKS_DIR = ROOT / "data" / "chunks"

# Gazette of India page layout, in PDF points (a page is 595 x 842).
# Body text sits between the margins, section titles sit in the margins.
HEADER_HEIGHT = 80
BODY_LEFT = 110
BODY_RIGHT = 485
MARGIN_NOTE_GAP = 8

# A section longer than this is split again, with overlap.
TOKENIZER = "o200k_base"
MAX_CHUNK_TOKENS = 800
CHUNK_OVERLAP_TOKENS = 100

DOWNLOAD_TIMEOUT = 60
