# Day 09 code

| File | What it shows |
|---|---|
| `parsing_chunking.ipynb` | **What parsing is**, the best tool for each type of file (digital PDF → PyMuPDF / `pymupdf4llm`, tables → pdfplumber, complex layout → Docling, Word → MarkItDown, web page → `<main>` + MarkItDown, scan → Tesseract, video → ffmpeg + Whisper), and **common cleaning patterns** (NFKC, quotes, invisible characters, hyphenation, broken lines, running headers, whitespace). No API key needed |
| `samples/bns_pages.pdf` | 5 real pages of the Bharatiya Nyaya Sanhita, 2023 (Gazette of India copy): page 1, then PDF pages 32–35 (sections 101–111) |
| `samples/bns_scanned.pdf` | Page 3 of the above as a tilted, blurred image, with no text layer |
| `samples/ipc_to_bns.pdf` | A ruled table: 6 old IPC sections and their new BNS sections |
| `samples/rental_agreement.docx` | A made-up rental agreement: headings, a table, a numbered list |
| `samples/section_103.html` | A blog page about BNS Section 103 with a nav bar, an ad, a sidebar and a footer |
| `samples/section_103.mp4` | A 33-second spoken explainer of Section 103 (macOS voice "Aman", en_IN) as a still-image video |

## Setup

```bash
brew install tesseract ffmpeg       # Windows: Tesseract from UB Mannheim, ffmpeg from ffmpeg.org
cd day-09/code
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

Open the notebook in VS Code (pick the `.venv` kernel) or run `jupyter notebook`.

**The first run downloads models** from Hugging Face: Docling's layout models (about 500 MB) and Whisper `base.en` (about 140 MB). The `docling`/`torch` install is also large. Run the notebook once before class.

## Notes (checked 2026-10-23)

- **Versions:** `pymupdf` 2.0, `pymupdf4llm` 2.0, `pdfplumber` 0.11.10, `docling` 2.142.1, `markitdown` 0.1.9, `faster-whisper` 1.2.1, Tesseract 5.5.3, Python 3.13.
- **`av<17` is pinned.** `faster-whisper` 1.2.1 calls `av.open(..., metadata_errors=...)`, and PyAV 19 no longer accepts that argument (`TypeError: open() got an unexpected keyword argument 'metadata_errors'`). PyAV 16.1.0 works.
- **`pymupdf4llm` 2.0** uses a layout model (`pymupdf-layout`) and runs OCR (RapidOCR) by itself on pages without text. `header=False, footer=False` drops running headers. Docs: https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/
- **Docling:** https://github.com/docling-project/docling. **MarkItDown:** https://github.com/microsoft/markitdown. **faster-whisper:** https://github.com/SYSTRAN/faster-whisper
- **The BNS PDF** is the Gazette of India copy (Act No. 45 of 2023, 25 Dec 2023), downloaded from PRS India: https://prsindia.org/files/bills_acts/bills_parliament/2023/The%20Bharatiya%20Nyaya%20Sanhita,%202023.pdf. The BNS came into force on 1 July 2024.
- **The IPC → BNS table** in `ipc_to_bns.pdf` was made for this class. Check an official comparison table before relying on it.
