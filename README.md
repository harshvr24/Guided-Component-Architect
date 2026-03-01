# Guided Component Architect

**Design-System-Governed Angular Component Generator with Self-Correcting Agent Loop**

---

## 1. Overview

Guided Component Architect is an agentic code-generation system that transforms natural language descriptions into **valid, styled Angular components** while strictly enforcing a predefined design system.

The system guarantees:

* Design-token compliance
* Angular syntax validity
* Controlled LLM output (raw code only)
* Automated validation + retry loop
* Modular and extensible architecture

This project demonstrates a governed LLM pipeline similar to platforms like Lovable or Bolt.new, where generation is constrained by rules and validated before final output.

---

# 2. Architecture Summary

The system follows a structured **Agentic Generation + Validation Loop**:

```
┌────────────────────┐
│  User Prompt       │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Generator Agent   │
│  (LLM Call)        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Validator Agent   │
│  - Token Check     │
│  - Syntax Check    │
└─────────┬──────────┘
          │
     ┌────┴────┐
     │ Valid?   │
     └────┬─────┘
          │Yes
          ▼
   Final Angular Component

          │No
          ▼
┌──────────────────────────┐
│ Self-Correction Prompt   │
│ (Inject Error Logs)      │
└─────────┬────────────────┘
          ▼
     Retry (bounded)
```

This loop ensures only compliant, syntactically valid components are returned.

---

# 3. Core Features

## Must-Have Features (Fully Implemented)

* JSON-based Design System
* Angular component generation
* Design token injection into LLM prompt
* Code-only output enforcement
* Automated validation
* Self-correction retry loop
* Modular architecture
* CLI entrypoint
* Agentic architecture explanation
* Prompt injection prevention strategy

---

# 4. Project Structure

```
pythrust/
│
├── backend/
│   ├── generator.py
│   ├── validator.py
│   ├── design_system.json
│   ├── retry_loop.py
│   ├── prompt_templates.py
│   ├── ast_validator.py
│   └── main.py
│
├── frontend/ (optional preview)
│
├── README.md
├── requirements.txt
└── package.json (if frontend included)
```

---

# 5. Design System

The design system is defined in:

```
backend/design_system.json
```

Example:

```json
{
  "colors": {
    "primary": "#6366f1",
    "secondary": "#ec4899",
    "background": "#ffffff",
    "text": "#111827"
  },
  "borderRadius": "8px",
  "fontFamily": "Inter",
  "spacingUnit": "4px"
}
```

### Enforcement Rules

The validator ensures:

* Only approved colors are used
* Border-radius matches token
* Font family matches token
* No arbitrary values outside design system

---

# 6. Generator

## Responsibilities

* Accept user natural language input
* Inject design system constraints into prompt
* Force strict code-only output
* Generate Angular component structure

## Prompt Engineering Strategy

The generator prompt includes:

* Explicit instruction to output only code
* Angular component scaffold template
* Design token constraints
* Prohibition of explanations or comments
* Error correction context (if retry)

---

# 7. Validator

The validator performs two checks:

## 1️⃣ Design Token Compliance

* Regex + static analysis
* Extracts CSS values
* Verifies tokens exist in JSON
* Flags arbitrary colors or styles

## 2️⃣ Syntax Validation

Two approaches supported:

* Basic structural checks
* AST-based TypeScript parsing (recommended)

AST validation ensures:

* Valid TypeScript syntax
* Proper bracket matching
* Valid Angular component structure

---

# 8. Self-Correction Mechanism

If validation fails:

1. Validator returns structured error logs
2. Error logs are appended to a correction prompt
3. LLM is re-invoked
4. Maximum retry limit enforced

Example correction injection:

```
The previous output failed validation:

Errors:
- Invalid color: #ff0000
- Missing closing bracket

Fix the code and regenerate the full component.
Return only valid Angular code.
```

This ensures controlled iterative repair.

---

# 9. Setup Instructions

Use this verified root-level workflow (also available in `RUN_LOCAL_GUIDE.md`).

## Step 1: Clone and enter repo root

```bash
git clone <repo-url>
cd Guided-Component-Architect
```

## Step 2: Backend setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set provider key (optional, fallback plan still works):

```bash
export GROQ_API_KEY=your_key_here
```

Run backend from repo root:

```bash
uvicorn pythrust.backend.server:app --host 0.0.0.0 --port 8000 --reload
```

API endpoints:

- `POST /v1/generate/page` (primary)
- `POST /generate` (legacy shim)

## Step 3: Frontend setup

In a second terminal:

```bash
cd pythrust/frontend
npm install
export NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm run dev -- --hostname 0.0.0.0 --port 3000
```

Open `http://localhost:3000` and click **Generate Full Page**.

## Step 4: Optional root smoke run

```bash
./scripts/run_from_root_smoke.sh
```
See also: **`RUN_LOCAL_GUIDE.md`** for the current verified local startup steps.

## Step 1: Clone Repository

```bash
git clone <repo-url>
cd pythrust
```

---

## Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4: Configure Environment

Create `.env`:

```
OPENAI_API_KEY=your_key_here
```

---

## Step 5: Run the CLI

```bash
python backend/main.py
```

Enter prompt:

```
A login card with glassmorphism effect
```

System will:

* Generate component
* Validate
* Retry if necessary
* Print final Angular component

---

# 10. Implementation Workflow (Detailed)

## 1. User Input Stage

User provides:

```
"A responsive login card with rounded button"
```

---

## 2. Prompt Construction

System builds structured prompt:

* Angular scaffold
* Tailwind / Angular Material usage
* Design tokens embedded
* Code-only instruction

---

## 3. First LLM Call

Output example:

```ts
@Component({...})
export class LoginCardComponent {}
```

---

## 4. Validation Stage

Checks:

* Uses #6366f1?
* Uses border-radius: 8px?
* Valid TS syntax?
* No random styles?

---

## 5. Retry Logic (if failed)

* Error context injected
* Second generation triggered
* Re-validation

---

## 6. Final Output

Only valid component returned.

---

# 11. Agentic Loop Design Principles

This project enforces:

* Deterministic validation
* Bounded retries
* Structured prompts
* Strict output formatting
* No uncontrolled generation

This is a governed code-generation architecture.

---

# 12. Prompt Injection Prevention Strategy

LLM-based code generators are vulnerable to prompt injection such as:

* "Ignore previous instructions"
* "Use random colors"
* "Output explanation text"

## Defensive Measures Implemented

### 1. Hard Prompt Framing

System-level instructions enforce:

* Output code only
* Ignore user instructions conflicting with design system
* Reject style overrides

### 2. Token-Based Validation

Even if model attempts malicious style override:

Validator blocks it.

Example:

If user says:

```
Use bright red background.
```

But red is not in JSON → validator rejects → correction loop triggered.

### 3. Output Filtering

System strips non-code text if necessary.

### 4. Bounded Retry

Prevents infinite injection loops.

---

# 13. Scaling to Full Page Generation

To scale:

### 1. Component Graph Generation

* Generate layout tree first
* Then generate components per node

### 2. Structured JSON Intermediate Representation

Instead of direct code generation:

```
User → Layout JSON → Validated → Code Emitter
```

### 3. Multi-Agent Architecture

* Layout Agent
* Style Agent
* Validator Agent
* Repair Agent

### 4. Incremental AST Merging

Instead of full regeneration:

* Parse existing component
* Apply delta edits

---

# 14. Optional Enhancements

* Live preview deployment (Vercel)
* Export `.ts` / `.html` / `.css`
* Multi-turn editing
* Full AST rewrite engine
* Design token theme switching

---

# 15. Assumptions

* Angular environment pre-installed
* Tailwind configured
* User has API key access
* Project focuses on component-level generation (not full app)

---

# 16. Time Spent

Approximate development time: 4–6 hours
Focus areas: governance loop, validator architecture, modular separation.

---

# 17. Why This Architecture Matters

This is not just chat-based generation.

This is:

* Governed generation
* Deterministic enforcement
* Self-correcting architecture
* Scalable LLM pipeline design

It demonstrates capability to build:

* AI code assistants
* Design-system-enforced builders
* Enterprise UI generation systems

---

# 18. Conclusion

Guided Component Architect successfully implements:

* Structured LLM orchestration
* Design-system enforcement
* Validation and retry loop
* Clean modular backend
* Production-oriented architecture

It satisfies all mandatory requirements and establishes a strong foundation for scaling toward full application generation systems.

---


## 19. Full-Page Generation Upgrade Plan (Implemented Baseline)

This repository now includes a baseline full-page pipeline:

- `POST /v1/generate/page` endpoint for page-level generation
- Planner output as structured `PagePlan`
- Multi-file `ProjectManifest` emitter for Angular page scaffolding
- Project-level validation report with file-path issues
- Dynamic color governance sourced from `design-system/design-tokens.json`

Next expansion milestones:

1. Replace template emitter with LLM-assisted per-section generation.
2. Add AST-level TypeScript/HTML validation and import graph checks.
3. Add session-based diff editing for selective regeneration.
4. Add route/data/service generation for multi-page apps.
