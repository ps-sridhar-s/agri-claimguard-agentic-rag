from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from agents.claim_workflow import ClaimAssessmentService
from evals.evaluator import run_eval_suite
from evals.ragas_evaluation import ragas_status
from src.architecture_status import architecture_status
from src.knowledge_base import get_knowledge_base
from src.schemas import ClaimRequest, EvalCase, HealthResponse, IngestResponse

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("agri_claimguard")

app = FastAPI(
    title="Agri ClaimGuard AI",
    description="Agentic RAG prototype for crop insurance claims intelligence.",
    version="1.0.0",
)


def cors_origins() -> list[str]:
    configured = os.environ.get("AGRICLAIMGUARD_CORS_ORIGINS", "")
    origins = [
        origin.strip()
        for origin in configured.split(",")
        if origin.strip()
    ]

    return origins or [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_ASSETS.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS), name="frontend-assets")

_service: ClaimAssessmentService | None = None


def get_service(force_rebuild: bool = False) -> ClaimAssessmentService:
    global _service

    if _service is None or force_rebuild:
        knowledge_base = get_knowledge_base(force_rebuild=force_rebuild)
        _service = ClaimAssessmentService(knowledge_base)

    return _service


def fallback_home() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Agri ClaimGuard AI</title>
        <style>
          :root { color-scheme: dark; }
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            background: #050505;
            color: #f8fafc;
            font-family: Inter, Segoe UI, Arial, sans-serif;
          }
          main {
            width: min(920px, calc(100vw - 32px));
            padding: 32px;
            border: 1px solid rgba(255,255,255,.14);
            border-radius: 24px;
            background: rgba(255,255,255,.055);
            box-shadow: 0 24px 80px rgba(0,0,0,.45);
          }
          h1 { margin: 0 0 12px; font-size: clamp(2rem, 7vw, 4.8rem); line-height: .95; }
          p { color: #cbd5e1; line-height: 1.7; }
          code, a { color: #38bdf8; }
          .grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); margin-top: 24px; }
          .card { border: 1px solid rgba(255,255,255,.1); border-radius: 16px; padding: 16px; background: rgba(0,0,0,.24); }
        </style>
      </head>
      <body>
        <main>
          <h1>Agri ClaimGuard AI</h1>
          <p>
            Backend is running. For the 3D React frontend, run
            <code>cd frontend && npm install && npm run dev</code>, or build it with
            <code>npm run build</code> to serve it from this FastAPI app.
          </p>
          <div class="grid">
            <a class="card" href="/docs">API docs</a>
            <a class="card" href="/health">Health</a>
            <a class="card" href="/architecture-status">Architecture status</a>
            <a class="card" href="/eval/status">Evaluation status</a>
          </div>
        </main>
      </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def home():
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)

    return HTMLResponse(fallback_home())


@app.get("/health", response_model=HealthResponse)
def health():
    knowledge_base = get_knowledge_base()
    return HealthResponse(
        status="ok",
        checks={
            "knowledge_base": knowledge_base.status(),
            "api": "running",
            "frontend_dist": FRONTEND_DIST.exists(),
        },
    )


@app.post("/ingest", response_model=IngestResponse)
def ingest(force_rebuild: bool = True):
    knowledge_base = get_knowledge_base(force_rebuild=force_rebuild)
    get_service(force_rebuild=True)

    return IngestResponse(
        indexed_documents=len(knowledge_base.documents),
        chunks=len(knowledge_base.chunks),
        vector_store_enabled=knowledge_base.vector_store_enabled,
        bm25_enabled=knowledge_base.bm25_enabled,
        message="Knowledge base ingestion completed.",
    )


@app.post("/query")
def query(claim: ClaimRequest):
    logger.info(
        "Incoming claim submission farmer=%s district=%s crop=%s policy=%s loss_reason=%s",
        claim.farmer_name,
        claim.district,
        claim.crop,
        claim.policy_id,
        claim.loss_reason,
    )
    assessment = get_service().assess(claim)
    logger.info(
        "Claim assessment completed request_id=%s recommendation=%s",
        assessment.request_id,
        assessment.recommendation.value,
    )
    return assessment


@app.get("/architecture-status")
def architecture():
    return architecture_status()


@app.get("/eval/status")
def eval_status():
    return {
        "deterministic_evals": "available",
        "metrics": [
            "citation_coverage",
            "groundedness_overlap",
            "keyword_coverage",
            "recommendation_match",
            "source_recall",
            "human_review_match",
            "agent_completion",
            "latency",
            "llm_faithfulness_judge",
        ],
        "ragas": ragas_status(),
    }


@app.post("/eval/run")
def run_evals(cases: list[EvalCase]):
    return run_eval_suite(cases, get_service())


@app.get("/{path:path}", include_in_schema=False)
def frontend_spa(path: str):
    if FRONTEND_INDEX.exists() and not path.startswith(("api/", "docs", "openapi.json")):
        return FileResponse(FRONTEND_INDEX)

    return HTMLResponse(fallback_home(), status_code=404)
