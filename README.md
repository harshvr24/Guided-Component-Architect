# 🚀 Guided Component Architect

An Agentic, Design-System-Governed UI Generation Platform.

Guided Component Architect is a structured AI-driven system that converts natural language UI descriptions into validated frontend components using a controlled, multi-stage backend pipeline.

The system enforces:

- Design system compliance
- Architectural governance
- Structured validation
- Self-correcting generation
- Controlled emission of artifacts

Unlike raw LLM code generation, this platform ensures deterministic, policy-compliant UI output.

---

# 📚 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Agentic Loop](#agentic-loop)
- [Project Structure](#project-structure)
- [Backend Modules](#backend-modules)
- [Frontend Application](#frontend-application)
- [Design System](#design-system)
- [Validation Pipeline](#validation-pipeline)
- [Retry & Self-Correction](#retry--self-correction)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Usage Flow](#usage-flow)
- [Configuration](#configuration)
- [Tech Stack](#tech-stack)

---

# 🧠 Overview

Guided Component Architect introduces an agent-based orchestration layer on top of AI code generation.

Instead of directly returning model output, the system:

1. Interprets intent  
2. Injects design constraints  
3. Generates structured component code  
4. Validates against policies  
5. Automatically retries on failure  
6. Emits only compliant results  

This mirrors real-world engineering workflows:

```

Specification → Implementation → Review → Fix → Release

```

---

# 🏗 Architecture

High-level system flow:

```

User Prompt
↓
Backend Agent
↓
Pipeline Execution
↓
Code Generation
↓
Validation Layer
↓
Retry Engine (if failed)
↓
Emitter
↓
Frontend Preview

```

The backend enforces governance before anything reaches the frontend.

---

# 🔁 Agentic Loop

The system runs a closed feedback loop:

### 1. Generation
`generator.py` creates component output using structured prompts.

### 2. Validation
Validators check:

- Syntax correctness
- Structural integrity
- Design token compliance
- Project-level rules

### 3. Failure Handling
If validation fails:

```

Generation → Fail → Error Explanation → Regenerate

```

### 4. Retry
`retry.py` feeds structured error messages back into generation.

### 5. Emission
Only validated output is exported through `emitter.py`.

This ensures reliability and controlled output quality.

---

# 📂 Project Structure

```

Guided-Component-Architect/
│
├── pythrust/
│   ├── backend/
│   ├── frontend/
│   └── design-system/
│       └── design-tokens.json
│
├── scripts/
├── requirements.txt
└── README.md

```

---

# ⚙ Backend Modules

Located in:

```

pythrust/backend

```

Core responsibilities include:

- Agent orchestration
- Pipeline execution
- Code generation
- Validation logic
- Governance enforcement
- Retry handling
- Emission control
- API server exposure

The backend ensures no uncontrolled model output is directly returned.

---

# 🖥 Frontend Application

Located in:

```

pythrust/frontend

```

Built with:

- Next.js
- TypeScript
- TailwindCSS

Responsibilities:

- User prompt input
- Display generation results
- Show retry attempts
- Visual preview of components

Frontend acts only as a presentation layer — logic lives in backend.

---

# 🎨 Design System

Located in:

```

pythrust/design-system/design-tokens.json

```

This file defines:

- Color tokens
- Spacing tokens
- Typography rules
- Component constraints

The backend injects these tokens into the generation process.

This guarantees:

- UI consistency
- Governance compliance
- Controlled styling

---

# ✅ Validation Pipeline

Validation is multi-layered.

| Layer | Purpose |
|--------|----------|
| Syntax | Code correctness |
| Structure | Schema compliance |
| Design | Token validation |
| Project | Architectural rules |

Only fully passing outputs move forward.

---

# 🔄 Retry & Self-Correction

The retry engine:

- Detects validation failures
- Generates structured error feedback
- Re-invokes generation
- Enforces retry limits

This produces a self-healing generation pipeline.

---

# 🛠 Installation

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm

---

## Clone Repository

```

git clone [https://github.com/harshvr24/Guided-Component-Architect.git](https://github.com/harshvr24/Guided-Component-Architect.git)
cd Guided-Component-Architect

```

---

## Backend Setup

```

python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt

```

---

## Frontend Setup

```

cd pythrust/frontend
npm install

```

---

# ▶ Running the Project

## Start Backend

```

cd pythrust/backend
python server.py

```

(If using alternative entrypoint)

```

python app.py

```

---

## Start Frontend

```

cd pythrust/frontend
npm run dev

```

Open:

```

[http://localhost:3000](http://localhost:3000)

```

---

# 🧪 Usage Flow

1. Enter a UI description
2. Backend agent processes request
3. Component is generated
4. Validators execute
5. Retry engine runs if needed
6. Final validated component is displayed

---

# ⚙ Configuration

Modify behavior via backend configuration files.

Design tokens can be updated in:

```

pythrust/design-system/design-tokens.json

```

Retry behavior and governance rules can be adjusted in backend modules.

---

# 🧰 Tech Stack

## Backend
- Python
- Structured Agent Pipeline
- Validation & Governance Layers

## Frontend
- Next.js
- TypeScript
- TailwindCSS

## AI Architecture
- Prompt-guided generation
- Self-correcting loop
- Design-system enforcement

---

# 🚀 Vision

Guided Component Architect aims to move beyond simple AI code generation into governed, reliable, and production-aligned UI automation.

Future expansion may include:

- Full page generation
- Multi-component orchestration
- AST-level validation
- Plugin validator system
- Enterprise design governance layers
```
