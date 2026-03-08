# Mémoire de Parfum 🌸

> *Where memories become fragrance*

An AI-powered fragrance experience that transforms a user's past, present, or future memories into a personalized, skin-safe scent composition — designed from emotions, personality, lifestyle, and sensory memories.

---

## Brief

Mémoire de Parfum was built for the L'Oréal AI competition. The core idea: scent is the most memory-linked of the five senses. We built a system that lets users choose a life moment they want to capture — a memory from the past, who they are in the present, or a future moment they want to design for — and translates that into a real fragrance blueprint made of top, heart, and base notes.

The system uses a hybrid AI pipeline: a fragrance knowledge graph (Neo4j) for structured reasoning, a vector store (Weaviate) for grounded explanations, and an LLM for generating the final personalized fragrance story. Guardrails are applied at every step to ensure safety, grounding, and no medical/therapeutic claims.

---

## Architecture Flow

```
User UI (Past / Present / Future + questionnaire + optional free text)
        │
        ▼
Signal Extraction          app/core/signal_extraction.py
(questionnaire → Scent Intent JSON via LLM)
        │
        ▼
GraphRAG                   app/graph/graph_rag.py
(Scent Intent JSON → emotion-to-note mapping via Neo4j knowledge graph)
        │
        ▼
Constraint Selector        app/core/constraint_selector.py
(candidates → final blueprint with compatibility + safety rules applied)
  ┌─────┴─────┐
  │ Guardrails │           app/guardrails/
  │ safety_rules.py        (banned ingredients, sensitivity constraints)
  │ schema_validator.py    (top/heart/base + safety note required)
  └────────────┘
        │
        ▼
Doc RAG                    app/rag/doc_rag.py
(blueprint notes → retrieve grounding references from Weaviate)
        │
        ▼
LLM Synthesis              app/core/llm_synthesis.py
(blueprint + references → final fragrance story)
  ┌─────┴─────┐
  │ Guardrails │
  │ grounding_rules.py     (output must cite retrieved facts)
  │ policy_rules.py        (no medical/therapeutic claims)
  └────────────┘
        │
        ▼
Guardrails + Logging + Evaluation + Feedback Memory
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend API | FastAPI (Python) |
| AI Orchestration | LangChain |
| LLM | OpenAI GPT-4o-mini (dev) / Claude 3.5 Sonnet (demo) |
| Knowledge Graph | Neo4j (Dockerized) |
| Vector Store | Weaviate (Dockerized) |
| Cache | Redis (Dockerized) |
| Database | PostgreSQL (Dockerized) |
| Observability | LangSmith |
| Infrastructure | Docker + Docker Compose |

---

## Project Structure

```
memoire-de-parfum/
│
├── .github/workflows/ci.yml          # GitHub Actions CI — lint, test, eval on push
├── docker-compose.yml                # Neo4j, Weaviate, Postgres, Redis
├── .env.example                      # Template — copy to .env and fill in keys
├── requirements.txt
│
├── app/
│   ├── main.py                       # FastAPI entry point, lifespan, routers
│   ├── config.py                     # Pydantic Settings — reads from .env
│   │
│   ├── api/
│   │   ├── deps.py                   # JWT auth dependency injection
│   │   └── routes/
│   │       ├── auth.py               # POST /auth/token — login, returns JWT
│   │       ├── questionnaire.py      # POST /questionnaire/extract — signal extraction only
│   │       ├── fragrance.py          # POST /fragrance/generate — full pipeline
│   │       ├── refine.py             # POST /refine/ — lighter/stronger/warmer/fresher
│   │       └── user.py               # GET+POST /user/blends — save and retrieve blends
│   │
│   ├── pipeline/
│   │   └── fragrance_pipeline.py     # Master orchestrator — wires all 5 steps together
│   │                                 # Also contains run_refinement_pipeline()
│   │
│   ├── core/
│   │   ├── signal_extraction.py      # Step 1 — questionnaire → Scent Intent JSON (LLM)
│   │   ├── constraint_selector.py    # Step 3 — candidates → Fragrance Blueprint JSON
│   │   └── llm_synthesis.py          # Step 5 — blueprint + refs → fragrance story (LLM)
│   │
│   ├── graph/
│   │   ├── neo4j_client.py           # Neo4j async driver, run_query(), run_write_query()
│   │   ├── graph_schema.cypher       # Cypher to seed the knowledge graph (run once)
│   │   └── graph_rag.py              # Step 2 — emotions → note candidates from Neo4j
│   │
│   ├── rag/
│   │   ├── weaviate_client.py        # Weaviate client, search_collection(), insert_document()
│   │   ├── ingest.py                 # Seeds 13 fragrance knowledge docs into Weaviate at startup
│   │   └── doc_rag.py                # Step 4 — blueprint notes → retrieved references from Weaviate
│   │
│   ├── guardrails/
│   │   ├── safety_rules.py           # Bans dangerous ingredients, sensitivity checks
│   │   ├── schema_validator.py       # Ensures blueprint has top/heart/base + safety note
│   │   ├── grounding_rules.py        # Ensures LLM output is anchored to retrieved references
│   │   └── policy_rules.py           # Blocks medical/therapeutic claims in generated text
│   │
│   ├── cache/
│   │   ├── redis_client.py           # Redis async client, get_cached(), set_cached()
│   │   └── cache_keys.py             # Deterministic cache key generation from intent hash
│   │
│   ├── auth/
│   │   ├── jwt.py                    # create_access_token(), verify_access_token()
│   │   └── rate_limit.py             # Per-user rate limiting via Redis (20 req/min)
│   │
│   ├── models/
│   │   ├── intent.py                 # Pydantic: ScentIntentJSON + all questionnaire schemas
│   │   ├── blueprint.py              # Pydantic: FragranceBlueprintJSON + FragranceNote
│   │   └── user.py                   # Pydantic: UserCreate, SavedBlend, SessionData
│   │
│   ├── db/
│   │   ├── postgres.py               # SQLAlchemy async engine, get_db(), init_db()
│   │   └── migrations/               # Alembic migrations
│   │
│   ├── observability/
│   │   ├── langsmith_tracer.py       # LangSmith setup — call once at startup
│   │   ├── trace_events.py           # Structured log events (graph hits, substitutions, blueprint)
│   │   ├── metrics.py                # Redis counters — generations, saves, refinements, cache hits
│   │   └── latency.py                # p50/p95 latency tracking per pipeline step
│   │
│   ├── evaluation/
│   │   ├── rubric.py                 # Scoring: relevance, coherence, safety, consistency, experiential
│   │   ├── eval_runner.py            # Runs test cases through pipeline, scores with rubric
│   │   └── test_cases/
│   │       ├── past_cases.json       # 3 Past frame test cases
│   │       ├── present_cases.json    # 3 Present frame test cases
│   │       └── future_cases.json     # 3 Future frame test cases
│   │
│   ├── feedback/
│   │   └── feedback_memory.py        # Stores user actions (save/refine/regenerate) in Redis
│   │
│   └── errors/
│       └── exceptions.py             # Full custom exception hierarchy + fallback messages
│
├── frontend/
│   ├── app.py                        # Streamlit entry — hero page, navigation
│   └── pages/
│       ├── 01_memory_frame.py        # Step 1 — choose Past / Present / Future
│       ├── 02_questionnaire.py       # Step 2 — dynamic questionnaire per frame
│       ├── 03_result.py              # Step 3 — fragrance blueprint + story display
│       └── 04_refine.py              # Step 4 — refine blend (lighter/stronger/warmer/fresher)
│
├── data/
│   └── safety_docs/                  # (Future) PDFs for Weaviate ingestion
│
└── tests/
    ├── unit/
    │   ├── test_signal_extraction.py
    │   ├── test_constraint_selector.py
    │   ├── test_guardrails.py
    │   └── test_cache_keys.py
    ├── integration/
    │   ├── test_pipeline_past.py
    │   ├── test_pipeline_present.py
    │   └── test_pipeline_future.py
    └── eval/
        └── test_eval_runner.py
```

---

## Key Design Decisions

**Hybrid retrieval over pure LLM** — GraphRAG handles structured reasoning (which notes map to which emotions) while Doc RAG handles grounded explanations (safety info, perfumery guidance). The LLM only synthesizes — it never invents facts.

**Constraint Selector before LLM** — the fragrance blueprint is fully determined before the LLM sees it. The LLM only writes the story, not the composition. This eliminates hallucinated note combinations.

**Guardrails as inline checks** — not a separate service. Safety rules run inside the Constraint Selector; grounding and policy rules run inside LLM Synthesis. Every step is gated.

**Cache before LLM calls** — identical questionnaire inputs return cached results instantly, reducing LLM cost and latency.

**Stubs for teammate modules** — `graph_rag.py` and `doc_rag.py` had working stubs during development so the pipeline could run end-to-end before those modules were complete.

---

## Getting Started

### Prerequisites
- Python 3.12+
- Docker Desktop

### Setup

```bash
# Clone and enter project
cd memoire-de-parfum

# Copy env template and fill in your keys
cp .env.example .env

# Start all services
docker-compose up -d

# Install dependencies
pip install -r requirements.txt
pip install "pydantic[email]"

# Start backend
uvicorn app.main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend
streamlit run app.py
```

### Required API Keys
- **OpenAI** — https://platform.openai.com (dev)
- **Anthropic** — https://console.anthropic.com (demo/production)
- **LangSmith** — https://smith.langchain.com (observability)

### Timeouts & troubleshooting
- **First fragrance creation can take 1–2 minutes**: the pipeline runs two LLM calls (signal extraction + synthesis), Neo4j, Weaviate, and Redis. The frontend allows up to 3 minutes; if you see "The request took too long", wait and retry or increase `LLM_REQUEST_TIMEOUT` in `.env` (default 90s per LLM call).
- **Ensure all services are up**: `docker-compose up -d` must be running so Neo4j, Weaviate, and Redis are available. Slow or missing services will cause long waits or failures.

---

## User Journey

```
1. Choose memory frame     Past / Present / Future
2. Answer questionnaire    5 questions tailored to the frame
3. Add free text           Optional memory description
4. Receive blueprint       Top / Heart / Base notes + fragrance story
5. Refine                  Lighter / Stronger / Warmer / Fresher
6. Save                    Store to personal scent memory profile
```

---

## Neo4j Knowledge Graph

The graph encodes three types of relationships:

- `(Emotion)-[:EVOKES]->(Note)` — which notes map to which emotions
- `(Note)-[:PAIRS_WITH]->(Note)` — note compatibility relationships  
- `(SafetyFlag)` — ingredients banned or restricted per sensitivity level

To seed the graph, run the Cypher in `app/graph/graph_schema.cypher` via the Neo4j browser at `http://localhost:7474`.

---

## Weaviate Vector Store

13 fragrance knowledge documents are automatically ingested at startup covering all notes across top, heart, and base layers. Each document contains experiential descriptions and safety guidance used to ground the LLM's output.

---

## Evaluation

Run the offline eval suite:

```bash
python -m app.evaluation.eval_runner
```

Scores each output on 5 dimensions: **relevance** (do notes match emotions?), **coherence** (are all layers present?), **safety** (no banned ingredients?), **consistency** (does the story mention the selected notes?), **experiential** (is framing experiential not medical?). Pass threshold is 0.7 overall.

---

*Built for the L'Oréal AI Competition — Mémoire de Parfum team*
