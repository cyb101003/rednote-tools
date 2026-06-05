# RealSkill Architecture

RealSkill is designed as a lightweight agentic content system. It combines a web studio, a FastAPI service, local retrieval memory, multi-agent drafting, judge selection, and a report view.

## System Overview

```text
User input
  topic + platform + optional style references
        |
        v
FastAPI application
  routes, validation, config status, health checks
        |
        v
Generation orchestration
  trend context + platform rules + language routing
        |
        v
Agent drafting panel
  Agent A + Agent B + Agent C
        |
        v
Judge and audit layer
  scoring + winner selection + risk signals
        |
        v
Publish cleanup
  markdown removal + final humanization path
        |
        v
Report page and API response
```

## Main Components

### Frontend

The frontend is built with static HTML, CSS, and JavaScript. This keeps the demo deployable on a small self-hosted server without a build pipeline.

Key pages:

- `frontend/landing.html`: product entry page.
- `frontend/index.html`: generation studio.
- `frontend/report.html`: report and share-card view.

The frontend handles:

- language switching,
- platform selection,
- configuration status checks,
- agent run loading state,
- report handoff through browser storage,
- copy and export actions.

### Backend

The backend uses FastAPI in `main.py`.

Core routes:

- `GET /`: landing page.
- `GET /app`: generation studio.
- `GET /report`: report page.
- `POST /generate`: multi-agent generation endpoint.
- `GET /config/status`: public-safe configuration status.
- `GET /health`: deployment health check.
- `GET /.well-known/skill.json`: skill discovery manifest.

The backend keeps configuration checks explicit. If generation is not configured, `/generate` returns a controlled service error instead of exposing internal details.

### Generation Pipeline

`core/generator.py` coordinates the generation flow:

1. Read user topic, platform, and optional references.
2. Resolve platform and default output language.
3. Retrieve local trend or style context when available.
4. Run three distinct writing agents.
5. Pass drafts into the judge layer.
6. Clean the selected result for direct publishing.
7. Return final copy, drafts, scores, audit signals, and report metadata.

### Agent Roles

Prompt logic lives in `agents/prompts.py`.

- Agent A focuses on viral hooks, platform rhythm, and scroll-stopping openings.
- Agent B focuses on lived-in detail, creator voice, and natural sharing tone.
- Agent C focuses on structure, clarity, usefulness, and user value.

The agents are intentionally different so the system can compare multiple creative strategies instead of producing three near-identical drafts.

### Judge Layer

`core/judge.py` evaluates drafts across practical content signals such as:

- platform fit,
- human tone,
- clarity,
- spread potential,
- originality,
- actionability.

The judge returns a selected winner, reasoning, score details, and audit signals. If model-based judging fails, the system can fall back to explainable local scoring rather than defaulting blindly to one agent.

### Publish Cleanup

`core/publish_cleaner.py` removes Markdown-like artifacts that users should not accidentally publish, such as bold markers, bullet prefixes, or formatting leftovers.

This step is important because the final output is intended to be copied directly into social platforms.

### Retrieval And Memory

RealSkill uses ChromaDB as local retrieval memory. The memory layer can store platform examples, trend notes, and style references. This lets the generator use contextual signals without hardcoding every writing pattern into one prompt.

Configured path:

```text
CHROMA_PATH=./chroma_db
```

### Internationalization

RealSkill separates UI language from output platform behavior.

- UI language can be switched across supported languages.
- Domestic platforms default toward Chinese output.
- Global platforms default toward conversational English output.
- Platform-specific prompt rules can be extended without changing the whole application.

This makes the product easier to adapt to additional regions, platforms, and creator markets.

## Deployment Shape

The current deployment is intentionally simple:

```text
Browser
   |
   v
FastAPI static routes + API routes
   |
   v
OpenAI-compatible model provider
   |
   v
Local Chroma memory
```

The same project can run locally, on a VPS, or behind a domain such as `realskill.asia`.

## Extension Points

RealSkill is structured so future development can add:

- new platform adapters,
- new language defaults,
- richer trend collectors,
- brand voice profiles,
- team workspaces,
- publish performance feedback,
- async generation jobs,
- cached trend retrieval,
- streaming progress updates.

The current implementation prioritizes a working end-to-end prototype while keeping the system modular enough for product iteration.
