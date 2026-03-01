# Step-by-step to-do list (systematic implementation)

Use this list to build or verify the Guided Component Architect in order.

---

## Step 1: Project structure and dependencies

**Goal:** Repo has a clear layout and all dependencies declared.

- Create root `requirements.txt` with FastAPI, uvicorn, openai, httpx (see `requirements.txt`).
- Create `design-system/` folder and leave space for the tokens file.
- Create `backend/` and `frontend/` folders.
- In `frontend/`, add `package.json` with Next.js, React, TypeScript (see `frontend/package.json`).

**Why:** So anyone can `pip install -r requirements.txt` and `npm install` in frontend and get a runnable stack.

---

## Step 2: Design system JSON

**Goal:** One source of truth for colors, radius, font, etc., used by both generator and validator.

- Create `design-system/design-tokens.json`.
- Include at least: `colors` (e.g. primary `#6366f1`), `border-radius` (e.g. `8px`), `typography` (e.g. font `Inter`).
- Optionally add spacing, shadows for richer prompts.

**Why:** The LLM and the Linter-Agent must share the same tokens so generation is governed and validation is deterministic.

---

## Step 3: Design system loader (backend)

**Goal:** Backend can load the JSON and format it for the prompt.

- In `backend/`, add `config.py` with the path to `design-tokens.json`.
- Add `design_system.py`: load JSON, format for prompt context, and expose a flattened set of “allowed values” for the validator.

**Why:** Keeps prompt-building and validation logic consistent and in one place.

---

## Step 4: Generator (LLM pipeline)

**Goal:** User prompt (+ optional previous code) → one Angular component (raw code only).

- Add `backend/generator.py`.
- System prompt: “You are an Angular expert. Output raw code only; use only the provided design tokens; use Angular Material and Tailwind.”
- User message: design system JSON + user prompt (+ optional previous code for multi-turn).
- Call OpenAI (or your LLM API); strip markdown code fences from the response.
- Require `OPENAI_API_KEY` (env or config).

**Why:** Prompt engineering and design context in the prompt are what make the output both code-only and design-system compliant.

---

## Step 5: Validator (Linter-Agent)

**Goal:** Automatically check generated code for token compliance and syntax.

- Add `backend/validator.py`.
- **Design tokens:** Regex (or simple parsing) to find hex colors, border-radius, font-family in the code; check they appear in the design system’s allowed values.
- **Syntax:** Bracket-matching for `()`, `[]`, `{}`, `<>` to catch unbalanced delimiters.
- Expose a single `validate(code)` that returns `(is_valid, list_of_errors)`.

**Why:** Automated checks are required; the self-correction loop needs concrete error messages to re-prompt the LLM.

---

## Step 6: Self-correction loop

**Goal:** If validation fails, re-prompt the LLM with the errors and retry.

- Add `backend/pipeline.py`.
- Flow: call generator → run validator. If valid, return code. If invalid, build a new “user” message that includes the original request plus the validation errors and (optionally) the last code; call generator again. Repeat up to N times (e.g. 2).
- Return the last code plus validation status/errors.

**Why:** This is the “agentic” part: the system fixes itself using the Linter-Agent’s feedback.

---

## Step 7: Backend API and preview extraction

**Goal:** One HTTP endpoint that runs the pipeline and returns code + preview.

- Add `backend/app.py` (FastAPI).
- POST `/api/generate`: body `{ "prompt", "previous_code"?: string }`. Call pipeline; return `{ code, preview_html?, valid, errors }`.
- Implement preview: from the generated `.ts`, extract `template` and `styles` (regex or simple parse); build a minimal HTML string (template + `<style>`) for iframe preview.
- CORS and error handling (400 for bad request, 500 for server errors).

**Why:** The frontend needs a single call to generate and to show a live preview without running Angular.

---

## Step 8: Frontend (Vercel app)

**Goal:** Minimal app with prompt input, generate, live preview, export, and multi-turn.

- Next.js app in `frontend/`: `app/layout.tsx`, `app/page.tsx`, `app/globals.css`, `next.config.js`, `tsconfig.json`.
- Page state: prompt, code, previewHtml, errors, loading.
- “Generate” button: POST to backend with `{ prompt }`; display code and errors; show preview in an iframe using `preview_html` (e.g. `srcDoc`).
- “Export .ts” button: download current `code` as a `.ts` file.
- “Apply as follow-up” (or multi-turn): send current `code` as `previous_code` with the new prompt (e.g. “Now make the button rounded”).
- Use `NEXT_PUBLIC_API_URL` for backend (default `http://localhost:8000`).

**Why:** Delivers the required “live preview”, “export”, and “multi-turn editing” in one place and is deployable on Vercel.

---

## Step 9: README and approach note

**Goal:** Clear run instructions and a short note on security and scaling.

- **README.md:** Describe the Agentic Loop (Generator → Validator → Self-Correction) with a small diagram or bullet list; project structure; how to run backend and frontend; design system location; assumptions (Tailwind/Material, standalone component, preview method).
- **APPROACH_NOTE.md (300–400 words):** (1) Prompt injection prevention: structured prompts, output validation, input sanitization/limits, no execution of user code. (2) Scaling to full-page apps: larger design system, structured output/schemas, chunked generation, versioned tokens, human-in-the-loop.

**Why:** Meets the assignment’s documentation and reflection requirements.

---

## Step 10: Final checks

- Run backend: `cd backend && pip install -r ../requirements.txt && set OPENAI_API_KEY=... && uvicorn app:app --port 8000`.
- Run frontend: `cd frontend && npm install && npm run dev`.
- Test: generate “A login card with glassmorphism”; then “Now make the button rounded”; export .ts; confirm preview and validation errors (if any) appear.
- Confirm `requirements.txt` and `frontend/package.json` are present and README + APPROACH_NOTE are complete.

**Why:** Ensures the system is runnable and that all must-haves are covered before submission.
