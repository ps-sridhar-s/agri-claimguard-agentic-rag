# AgriClaimGuard Frontend (Vite + React)

This is a minimal frontend prototype to demo a 3D scene with a claim form that calls the FastAPI backend.

## Quick start

1. Install dependencies

```bash
cd frontend
npm install
```

2. Run the backend (from repo root)

```bash
# ensure venv is active
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

3. Run frontend

```bash
cd frontend
npm run dev
```

Open the Vite dev URL (usually http://localhost:5173). The form posts to `http://127.0.0.1:8000/query`.

## Notes
- CORS is enabled for `http://localhost:5173` in `app.py` for development.
- The 3D scene is implemented with `@react-three/fiber` and shows a rotating box whose color reflects the recommendation.
- For a production-ready UI, expand components, add authentication, and polish visuals/animations.
