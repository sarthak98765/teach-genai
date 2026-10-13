# Day 04: Prompt & context engineering

**One idea for the whole day:** a good prompt is a spec, not a wish. It has seven blocks: **Role, Instruction, Context, Input, Output format, Guardrails, Workflow**. Then you *measure* it, because a prompt you haven't measured is a guess.

Open the diagrams in https://excalidraw.com (File → Open) or the VS Code Excalidraw extension. Code setup is in [`code/README.md`](code/README.md).

## Class flow (60 min)

| # | Topic | Diagram | Code | Min |
|---|---|---|---|---|
| 1 | The 7 blocks of a good prompt | `prompt-anatomy` | `01_prompt_anatomy.ipynb` demo 1 | 8 |
| 2 | Real production prompts, block by block | `real-prompt-exim-router`, `real-prompt-exam-extraction` | - | 7 |
| 3 | System / user / assistant roles, few-shot | `roles-and-few-shot` | `01` demos 2-3 | 5 |
| 4 | XML tags / delimiters, clear output spec | `delimiters-and-output-spec` | `01` demo 4 | 5 |
| 5 | Chain-of-thought vs built-in reasoning | `cot-vs-reasoning` | `02_reasoning_and_chaining.ipynb` part A | 5 |
| 6 | Prompt chaining | `prompt-chaining` | `02` part B | 5 |
| 7 | Context engineering: what goes in, in what order | `context-engineering` | `03_context_and_caching.ipynb` part A | 5 |
| 8 | Prompt caching | `prompt-caching` | `03` part B | 5 |
| 9 | **Live build:** messy extraction, 3 iterations, 10 examples | `prompt-iteration-loop` | `04_extraction_lab.ipynb` | 15 |

## Colour code (same in every diagram)

| Block | Colour |
|---|---|
| Role | blue |
| Instruction | violet |
| Context | green |
| Input | cyan |
| Output format | orange |
| Guardrails | red |
| Workflow | yellow |
| Examples (few-shot) | purple |

## Homework

1. Add 3 nastier messages to `code/orders.py` (two orders in one message, "same as last week", a voice-note transcript) with gold answers. Does v3 still score 100%? Fix it as v4 and log the change.
2. Rewrite one prompt from your day job using the 7 blocks. Keep a prompt log: version · change · result.

## Sources (checked 2026-10-13)

- Claude prompting best practices (XML tags, examples, long context): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic, Effective context engineering for AI agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- OpenAI reasoning guide: https://developers.openai.com/api/docs/guides/reasoning
- OpenAI prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching
- Claude prompt caching: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- OpenAI pricing: https://developers.openai.com/api/docs/pricing
- OpenAI Model Spec (chain of command): https://model-spec.openai.com
