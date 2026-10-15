import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv(Path(__file__).parent / ".env")
MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
OCR_MODEL = "mistral-ocr-latest"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")

def pdf_to_md(pdf_path: str) -> str:
    """OCR a local PDF with Mistral and save its markdown as test_output/<pdf_name>.md; returns the saved path."""
    name = os.path.splitext(os.path.basename(pdf_path))[0]
    with Mistral(api_key=MISTRAL_API_KEY) as mistral:
        with open(pdf_path, "rb") as f:
            uploaded = mistral.files.upload(file={"file_name": os.path.basename(pdf_path), "content": f.read()}, purpose="ocr")
        try:
            signed = mistral.files.get_signed_url(file_id=uploaded.id, expiry=1)
            response = mistral.ocr.process(model=OCR_MODEL, document={"type": "document_url", "document_url": signed.url})
        finally:
            mistral.files.delete(file_id=uploaded.id)
    markdown = "\n\n---\n\n".join(f"<!-- page {page.index + 1} -->\n\n{page.markdown or ''}" for page in response.pages or [])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{name}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    return out_path

if __name__ == "__main__":
    out = pdf_to_md(sys.argv[1])
    print(open(out, encoding="utf-8").read())
    print(f"\nSaved to {out}")