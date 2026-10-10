"""Day 02 demo 2: same prompt, temperature 0 vs temperature 1.

Sends the same prompt several times at each temperature and prints every answer,
plus the input/output tokens each call used.

Model: gpt-6-luna with reasoning turned off. OpenAI's reasoning models only accept
temperature / top_p when reasoning effort is "none"; otherwise the API returns a 400.
OpenAI does not offer top_k (Claude and Gemini do).

Run:
    python temperature_demo.py                      # temperature 0 vs 1, 3 runs each
    python temperature_demo.py --runs 5
    python temperature_demo.py --top-p 0.1          # add top_p to both runs
    python temperature_demo.py --prompt "Write a one-line tagline for a chai shop."
"""

import argparse
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gpt-6-luna"
DEFAULT_PROMPT = "Give me three creative names for an AI startup. Only the names, one per line."


def ask(client: OpenAI, prompt: str, temperature: float, top_p: float | None, max_tokens: int):
    response = client.responses.create(
        model=MODEL,
        input=prompt,
        reasoning={"effort": "none"},  # sampling settings only work with reasoning off
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_tokens,
    )
    return response.output_text.strip(), response.usage, response.status


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare temperature 0 vs 1 on the same prompt.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--runs", type=int, default=3, help="calls per temperature")
    parser.add_argument("--top-p", type=float, default=None, help="optional: only sample from the top tokens covering this much probability")
    parser.add_argument("--max-tokens", type=int, default=200, help="output budget per call (OpenAI minimum is 16)")
    args = parser.parse_args()

    client = OpenAI()  # reads OPENAI_API_KEY from .env
    total_in = total_out = 0

    print(f"Model : {MODEL}")
    print(f"Prompt: {args.prompt}")
    if args.top_p is not None:
        print(f"top_p : {args.top_p}")

    for temperature in (0.0, 1.0):
        print(f"\n{'=' * 20} temperature = {temperature} {'=' * 20}")
        for run in range(1, args.runs + 1):
            text, usage, status = ask(client, args.prompt, temperature, args.top_p, args.max_tokens)
            total_in += usage.input_tokens
            total_out += usage.output_tokens
            print(f"\n--- run {run} (input {usage.input_tokens} tokens, output {usage.output_tokens} tokens) ---")
            print(text)
            if status == "incomplete":
                print("[cut off: hit --max-tokens]")

    print(f"\nTotal tokens used: {total_in} input + {total_out} output")
    print("Compare: temperature 0 is more repeatable (not always identical), temperature 1 varies more.")


if __name__ == "__main__":
    main()
