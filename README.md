# Generative & Agentic AI Engineering: 35 days

A hands-on course for AI engineering: LLMs, prompts and context, tool calling, RAG, evals, agents, MCP, voice, and shipping it all to production. By the end there are 3 deployed portfolio projects.

- **Stack:** TypeScript (Next.js + Vercel AI SDK) for products and UI, and Python (LangGraph + FastAPI) for agents.

## Weeks
| Week | Days | Theme |
|---|---|---|
| 1 | 01–07 | Foundations: how LLMs work, model choice, prompts/context, structured output, tool calling, streaming UI, multimodal |
| 2 | 08–14 | RAG + evals → ship P1 DocuMind |
| 3 | 15–21 | Agents: from scratch, frameworks, LangGraph, memory, HITL, multi-agent → ship P2 Deep Research Agent |
| 4 | 22–28 | MCP, coding/browser agents, observability, security, deployment + cost |
| 5 | 29–35 | Voice agents, fine-tuning, ship P3 Commerce Copilot, portfolio, interviews, demo day |

## Projects
| # | Project | Stack | What you ship |
|---|---|---|---|
| P1 | **DocuMind**: production RAG SaaS | Next.js, Vercel AI SDK, Postgres + pgvector, hybrid search, reranker, promptfoo | Upload docs → parse/chunk/embed → streamed answers with citations; hybrid search + reranking; multi-tenant; eval suite in CI |
| P2 | **Deep Research Agent** (multi-agent) | LangGraph, FastAPI, web search APIs, Postgres, Langfuse, Docker; Next.js front end | Topic → research plan → human approval → parallel workers → cited report; memory, tracing, agent evals, budget cap |
| P3 | **Commerce Copilot**: MCP server + chat + voice | MCP TS SDK over an Express/MongoDB store, Next.js + AI SDK chat, voice agent framework, Docker | Remote MCP server with OAuth powering desktop clients, a chat copilot and a voice agent; refunds need human approval; guardrails |