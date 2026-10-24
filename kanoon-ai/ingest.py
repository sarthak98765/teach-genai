import json
import sys

from chunk import chunk_act
from config import CHUNKS_DIR, PARSED_DIR
from download import download
from logger import custom_logger
from parse import to_markdown
from sources import ACTS


def ingest(act_id: str) -> None:
    """download -> parse -> chunk for one Act. Writes data/parsed/<act>.md and data/chunks/<act>.jsonl."""
    markdown = to_markdown(download(act_id))
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    (PARSED_DIR / f"{act_id}.md").write_text(markdown)

    chunks = chunk_act(act_id, markdown)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHUNKS_DIR / f"{act_id}.jsonl", "w") as f:
        f.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks)
    custom_logger.info(f"ingest | {act_id}: done")


if __name__ == "__main__":
    for act_id in sys.argv[1:] or ACTS:
        ingest(act_id)
