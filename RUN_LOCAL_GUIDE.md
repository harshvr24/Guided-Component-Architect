# Run Guided Component Architect Locally (Step-by-Step)

This guide is the up-to-date local startup flow for the current repository state.

## 1) Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## 2) Clone and open repo

```bash
git clone <your-repo-url>
cd Guided-Component-Architect
```

## 3) Backend setup (Terminal 1)

### 3.1 Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3.2 Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3.3 Configure env var (optional but recommended)

The planner/generator reads `GROQ_API_KEY` at runtime.

```bash
export GROQ_API_KEY="your_groq_api_key"
```

Windows PowerShell:

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

> If missing, the backend can still return a safe fallback plan.

### 3.4 Start backend API

```bash
uvicorn pythrust.backend.server:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```bash
curl -sS http://127.0.0.1:8000/docs | head
```

## 4) Frontend setup (Terminal 2)

```bash
cd pythrust/frontend
npm install
```

Set backend URL (recommended):

```bash
export NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"
```

Windows PowerShell:

```powershell
$env:NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"
```

Start frontend:

```bash
npm run dev -- --hostname 0.0.0.0 --port 3000
```

Open: `http://localhost:3000`

## 5) End-to-end test

1. In UI, enter a prompt like: `Build a marketing page with hero, features, pricing and footer`.
2. Click **Generate Full Page**.
3. Confirm:
   - Generated files list populates.
   - Code viewer shows selected file content.
   - Live preview appears.
   - Validation panel shows issues/warnings if present.

## 6) API-only test

```bash
curl -sS -X POST http://127.0.0.1:8000/v1/generate/page \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Build a full page app with hero and footer"}' | python -m json.tool | head -n 80
```

## 7) Common issues

### "Unable to reach backend"
- Ensure backend is running on port `8000`.
- Ensure `NEXT_PUBLIC_API_URL` points to the backend URL.

### CORS errors
- Use the recommended backend startup command (`pythrust.backend.server:app`).
- Verify preflight:

```bash
curl -i -X OPTIONS http://127.0.0.1:8000/v1/generate/page \
  -H 'Origin: http://127.0.0.1:3000' \
  -H 'Access-Control-Request-Method: POST'
```

### Missing dependencies
- Re-run `pip install -r requirements.txt` and `npm install`.

## 8) Production build checks

Frontend:

```bash
cd pythrust/frontend
npm run build
```

Backend syntax check:

```bash
python -m compileall pythrust/backend
```
