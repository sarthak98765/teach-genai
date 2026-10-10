"""Day 02 demo 1: see how text turns into tokens and token IDs.

Uses tiktoken (OpenAI's open-source tokenizer). It runs locally: no API key, no cost.
Other model families (Claude, Gemini, Llama) use their own tokenizers, so their
exact counts differ, but the idea is the same.

Run:
    python count_tokens.py                      # built-in examples
    python count_tokens.py "your text here"     # your own text
    python count_tokens.py --file prompt.txt    # a whole file
"""

import argparse
import tiktoken

# o200k_base is the encoding used by OpenAI's recent models (GPT-4o and later).
ENCODING = "o200k_base"

EXAMPLES = {
    "English": "I love machine learning!",
    "Hindi (Devanagari)": "मुझे मशीन लर्निंग बहुत पसंद है!",
    "Hinglish": "Mujhe machine learning bahut pasand hai!",
    "Python code": "def add(a, b):\n    return a + b",
    "Rare word": "Pneumonoultramicroscopicsilicovolcanoconiosis",
}


def show(label: str, text: str, enc: tiktoken.Encoding) -> int:
    ids = enc.encode(text)
    pieces = [enc.decode([i]) for i in ids]
    print(f"\n=== {label} ===")
    print(f"Text: {text!r}")
    print(f"Characters: {len(text)}")
    print(f"Words: {len(text.split())}")
    print(f"Tokens: {len(ids)}")
    print(f"Pieces: {pieces}")
    print(f"Token IDs: {ids}")
    return len(ids)


def main() -> None:
    parser = argparse.ArgumentParser(description="Count tokens in text.")
    parser.add_argument("text", nargs="?", help="text to tokenize")
    parser.add_argument("--file", help="path to a text file to tokenize")
    args = parser.parse_args()
    enc = tiktoken.get_encoding(ENCODING)
    print(f"Tokenizer: {ENCODING}")
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
        ids = enc.encode(text)
        print(f"\n{args.file}: {len(text)} characters, {len(ids)} tokens")
        return
    if args.text:
        show("Your text", args.text, enc)
        return
    counts = {label: show(label, text, enc) for label, text in EXAMPLES.items()}
    print("\n=== Summary ===")
    for label, n in counts.items():
        print(f"{label:<20} {n:>3} tokens")
    print("\nSame meaning, different token counts: tokens depend on the tokenizer, not the meaning.")


if __name__ == "__main__":
    main()