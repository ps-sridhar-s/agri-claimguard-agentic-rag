# Agri ClaimGuard AI

Agentic RAG platform for crop insurance claim assessment. The project combines a FastAPI backend, LangGraph-style agents, hybrid retrieval, deterministic evaluation, and a premium 3D React frontend for claim review workflows.

## Features

- FastAPI backend with `/query`, `/ingest`, `/health`, `/architecture-status`, and evaluation endpoints.
- Agent workflow for claim, policy, weather, historical, evidence, reasoning, and compliance checks.
- Hybrid retrieval with Milvus Lite semantic search, BM25 sparse retrieval, and Reciprocal Rank Fusion ranking.
- Citation-backed claim recommendations with audit events.
- Deterministic evaluation suite with RAGAS-compatible export rows.
- Vite React frontend with Three.js, React Three Fiber, Framer Motion, glass UI, animated LangGraph workflow, AI console, claim form, analytics, and evidence panels.
- Local-first development flow for notebooks, backend API testing, and frontend iteration.

## Project Structure

```text
.
|-- agents/                  # Agent tools and LangGraph-style agent definitions
|-- app.py                   # FastAPI application
|-- evals/                   # Evaluation runner and metric implementations
|-- frontend/                # Vite + React + Three/Fiber UI
|-- models/                  # Chat and embedding client factories
|-- orchestrator/            # Multi-agent orchestration graph
|-- src/                     # Retrieval, vector storage, schemas, KB, audit utilities
|-- tests/                   # Pytest suite
|-- requirements.txt         # Python dependencies
`-- README.md
```

## Prerequisites

- Python 3.11+ recommended.
- Node.js 18+ for the frontend.
- Ollama running locally if you use the default local chat and embedding clients.
- Milvus Lite is used through `pymilvus` for local vector storage.

The current default model clients use:

```text
Chat:      Ollama model llama3.1:8b
Embedding: Ollama model mxbai-embed-large
```

Install/pull those models if needed:

```bash
ollama pull llama3.1:8b
ollama pull mxbai-embed-large
```

## Backend Setup

From the repository root:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL:

```text
http://localhost:5173
```

The frontend posts claims to:

```text
http://127.0.0.1:8000/query
```

CORS is already enabled for:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Build the frontend:

```bash
cd frontend
npm run build
```

After `npm run build`, FastAPI will serve the built React app from:

```text
http://127.0.0.1:8000
```

Preview the production build:

```bash
npm run preview
```

## Ingest Knowledge Base

The backend can build or rebuild its knowledge base:

```bash
curl -X POST "http://127.0.0.1:8000/ingest?force_rebuild=true"
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/ingest?force_rebuild=true"
```

The response includes indexed document count, chunk count, and whether vector/BM25 retrieval is enabled.

## Query Claim API

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_name": "Ram Kumar",
    "district": "Anantapur",
    "crop": "Groundnut",
    "date_of_loss": "2025-08-15",
    "loss_reason": "Drought",
    "policy_id": "PMFBY-2025",
    "query": "What is the eligibility for drought compensation?"
  }'
```

PowerShell:

```powershell
$body = @{
  farmer_name = "Ram Kumar"
  district = "Anantapur"
  crop = "Groundnut"
  date_of_loss = "2025-08-15"
  loss_reason = "Drought"
  policy_id = "PMFBY-2025"
  query = "What is the eligibility for drought compensation?"
} | ConvertTo-Json

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/query" -ContentType "application/json" -Body $body
```

## Retrieval Notes

Hybrid retrieval lives in `src/retrieval.py`.

Current flow:

1. Embed the user query.
2. Search Milvus Lite collection `crop_insurance`.
3. Retrieve BM25 matches from persisted chunks.
4. Fuse semantic and sparse rankings with Reciprocal Rank Fusion.
5. Return LangChain `Document` objects.

Notebook example:

```python
import importlib
import src.retrieval
importlib.reload(src.retrieval)

results = src.retrieval.hybrid_retriever(
    "What is the eligibility for drought compensation?"
)

for doc in results:
    print(doc.page_content)
    print(doc.metadata)
```

Use `doc.page_content`, not `hit["entity"]["text"]`, because `hybrid_retriever()` returns `Document` objects.

## Run Tests

Run all tests:

```bash
python -m pytest tests -q
```

Run focused suites:

```bash
python -m pytest tests/test_retrieval.py -q
python -m pytest tests/test_policy_agent.py -q
python -m pytest tests/test_schemas.py -q
```

## Run Evaluations

Run the CLI evaluation suite:

```bash
python -m evals.run_evals
```

This writes:

```text
storage/eval_reports/latest_eval_report.json
storage/eval_reports/latest_ragas_rows.json
```

Evaluation endpoints:

```text
GET  /eval/status
POST /eval/run
```

Metrics include citation coverage, groundedness overlap, expected keyword coverage, source recall, recommendation match, human review match, agent completion, latency, and optional LLM faithfulness judging.

## Environment Variables

Optional variables:

```text
OPENWEATHER_API_KEY
folder_path
AGRICLAIMGUARD_ENABLE_VECTOR=true
AGRICLAIMGUARD_ENABLE_LIVE_AGENTS=true
nvidia_embedding_key
nvidia_embedding_model
nvidia_chat_key
nvidia_chat_model
```

The current checked-in model factories default to local Ollama clients. NVIDIA environment variables are present for alternate model paths in the codebase, but the active default is local Ollama.

## Troubleshooting

### Milvus collection is released

If you see:

```text
Collection 'crop_insurance' is in state 'released'; call load() before search/get/query
```

Restart the notebook kernel or backend process so the latest `src.retrieval` and `src.vector_storage` code is loaded. The code now loads and retries the collection before search.

### Milvus LOCK permission error

If you see:

```text
PermissionError: milvus.db\LOCK
```

Another process is using the local Milvus Lite database. Stop FastAPI, close notebooks/kernels that opened Milvus, then retry. Milvus Lite expects one local process to own the DB lock.

### Frontend cannot call backend

Check that both are running:

```text
Backend:  http://127.0.0.1:8000
Frontend: http://localhost:5173
```

The frontend sends requests to `http://127.0.0.1:8000/query`.

### npm not found

Install Node.js 18+ and reopen the terminal so `node` and `npm` are on PATH.

## Deployment Notes

Backend:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn app:app --host 0.0.0.0 --port $PORT
```

Frontend:

```bash
cd frontend
npm install
npm run build
```

Keep local development artifacts out of deployment:

```text
.env
.venv/
__pycache__/
.pytest_cache/
milvus.db/
storage/
test notebooks with secrets
```

For production, use a managed vector database or isolated persistent volume instead of sharing a local Milvus Lite DB across processes.
