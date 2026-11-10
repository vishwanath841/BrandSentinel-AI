# BrandSentinel AI
### Intelligent Pre-Publication Brand Governance & Content Compliance Platform
**Enterprise Release v1.0 • Lead Developer: Vishwanath S A (GM Institute of Technology)**  
**GitHub Repository:** [github.com/vishwanath841/BrandSentinel-AI](https://github.com/vishwanath841/BrandSentinel-AI)

> **Core Promise:** *Every piece of content should sound, look, and feel like the same brand — before it ever reaches the public.*

---

## 1. Overview & Problem Statement

Modern organizations publish content across dozens of distributed creators, agencies, and generative AI tools. Without centralized pre-publication governance, teams inadvertently introduce:
- **Inconsistent Tone & Voice:** Aggressive, informal, or off-brand messaging that dilutes reputation.
- **Prohibited & Outdated Terminology:** Deprecated product nomenclature, competitor disparagement, or forbidden buzzwords.
- **Unsupported & Conflicting Claims:** Exaggerated uptime statistics, false superlatives, or unverified regulatory certifications that create legal liability.
- **Visual & Accessibility Drift:** Deviations from approved brand palettes and low-contrast typography failing WCAG standards.

**BrandSentinel AI** is an intelligent, multi-tier brand governance platform that evaluates text, documents (PDF, Word DOCX), and graphics against an organization's approved Brand DNA. It flags policy deviations with precise evidence citations, formulates intent-preserving smart rewrites, and maintains an immutable human-in-the-loop review audit trail.

---

## 2. Technology Stack & Lightweight Architecture

Engineered to operate with high responsiveness and low resource consumption on standard environments (including 8GB RAM machines):

| Layer | Technology | Primary Responsibility |
|---|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons | High-performance dashboard, dedicated AI Document Briefing, interactive diffs, and live preview |
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy, Pydantic | Asynchronous REST API, multimodal ingestion, scoring engines, and audit ledger |
| **Database** | SQLite / PostgreSQL | Structured persistence for Brand DNA profiles, terminology rules, approved facts, and audit logs |
| **High-Tier AI Engine** | NVIDIA NIM (`nemotron-3.5-120b`), Google Gemini (`gemini-2.5-flash`) | Deep contextual policy reasoning, multimodal analysis, and semantic revision synthesis |
| **Local / Edge LLM** | Ollama / LM Studio (OpenAI-compatible) | Self-hosted, air-gapped LLM inference for sovereign enterprise deployments |
| **Contextual Semantic NLP** | Custom Deterministic & Heuristic Engine | Zero-dependency local inspection ensuring 100% platform uptime even when offline |
| **Document Processing** | PyMuPDF (`fitz`), `python-docx` | Page-by-page text extraction, structural paragraph parsing, and metadata analysis |
| **Visual Brand Inspector** | OpenCV (`cv2`), NumPy, PIL, OCR | K-Means color clustering, $\Delta E$ Euclidean distance, and WCAG 4.5:1 contrast calculations |

---

## 3. Core Capabilities & Platform Features

### 3.1 AI Document Summary & Executive Briefing
Every document inspection immediately presents a dedicated, multi-pillar executive intelligence view:
- **Scope & Content Profile (What the Document Contains):** Synthesizes core themes, target audience, structural composition (word count, reading duration, section count), and source excerpts.
- **Compliance Diagnosis & Risk Inventory (What Was Found):** Breakdown of prohibited vocabulary, unverified claims, voice slips, and validated governance strengths.
- **Strategic Publication Roadmap (What We Need to Do):** Clear, numbered operational guidance directing reviewers through smart rewrite approvals, claim substantiation, and final sign-off.

### 3.2 Sub-Navigation Workspace Views
Audited submissions feature high-visibility tabbed navigation:
- **📑 AI Document Summary & Briefing:** High-level executive synthesis, scores, and roadmap.
- **🔍 Audit Findings & Smart Suggestions:** Interactive table with category and severity filters, evidence citations, and side-by-side revision diffs.
- **🛡️ ClaimGuard Fact Verification:** Factual claims ledger classifying statements against verified company records.
- **📄 Document Reader & Extracted Text:** Complete document reader with search, paragraph numbering, copy-to-clipboard, and flagged phrase badges.
- **🎨 Visual Brand Inspector:** Dominant palette extraction and WCAG accessibility contrast checks (for image uploads).

### 3.3 ClaimGuard & The Reliability Principle
- **Strict Reliability Principle:** The platform distinguishes verified violations from uncertain findings. It never claims a promotional statement is false solely because supporting evidence was not found; it designates it as `UNSUPPORTED_NEEDS_REVIEW`.
- **Classification Categories:**
  - `VERIFIED`: Statement is fully substantiated by approved corporate facts.
  - `CONTRADICTION`: Claim directly contradicts approved facts (e.g., claiming "99.999% SLA" when approved SLA is "99.99%").
  - `UNSUPPORTED_NEEDS_REVIEW`: High-impact promotional claims or unverified statistics requiring human sign-off.
  - `COMPLIANT`: Factual statements adhering to established standards.

### 3.4 Intent-Preserving Smart Rewriter
- Formulates corrections that fix prohibited terminology, competitor disparagement, or tone slips **while strictly preserving the author's original promotional context and value proposition**.

### 3.5 Sentinel AI Copilot (Interactive Chatbot)
- Floating assistant embedded across the platform.
- Connected directly to active Brand DNA, terminology dictionaries, and ClaimGuard knowledge bases for instant Q&A, SLA verification, and live copy rewriting.

### 3.6 Human Review & Approval Workflow
- Authorised reviewers can interactively:
  - **Accept** a suggested revision (updating document text).
  - **Edit** a suggestion inline to adjust phrasing.
  - **Reject** a suggestion with review notes.
- **Final Publication Gate:** Renders formal decisions (`APPROVED`, `CHANGES_REQUESTED`, `REJECTED`) recorded in an immutable audit ledger.

### 3.7 Audit History Management
- **Single Item Deletion:** Remove individual submissions with associated records.
- **Bulk Clear All:** One-click history purge with disk cleanup for temporary uploads.

### 3.8 Brand Drift Analytics
- Tracks compliance trends across submissions.
- Surfaces top recurring violations, claim verification hotspots, and proactive recommendations to update brand documentation.

---

## 4. Multi-Tier Resilient AI Architecture

BrandSentinel AI utilizes a 3-tier cascade ensuring the platform operates seamlessly in any environment:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Cloud LLM (NVIDIA NIM / Google Gemini)             │
│ High-throughput reasoning & intent-preserving rewrites      │
└──────────────────────────────┬──────────────────────────────┘
                               │ (if unavailable or offline)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Tier 2: Self-Hosted / Local LLM (Ollama / LM Studio)        │
│ Air-gapped OpenAI-compatible local model inference          │
└──────────────────────────────┬──────────────────────────────┘
                               │ (if local server unreachable)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Tier 3: Contextual Semantic NLP Engine                      │
│ Built-in, zero-dependency deterministic & heuristic rules   │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Security & Privacy Hardening

- **Zero API Key Leakage:** Sensitive tokens (NVIDIA, Gemini) are stored strictly in server environment configurations. Frontend settings and API responses mask keys (`•••••••• (Encrypted & Active)`).
- **Path Traversal Protection:** File uploads sanitize original filenames using `Path(file.filename).name` prepended with unique UUIDs, preventing directory traversal attacks.
- **Repository Safety:** The `.gitignore` configuration guarantees that `.env`, databases (`*.db`), and uploaded files (`backend/uploads/*`) are excluded from version control.

---

## 6. Quick Start & Local Execution

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 6.1 Single-Script Launch (Windows PowerShell)
```powershell
# From the project root
.\start.ps1
```
*(Or use `start.bat` in Command Prompt)*

### 6.2 Manual Setup

**Terminal 1 — Backend Server:**
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend Development Server:**
```powershell
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** (API requests are automatically proxied to port 8000).

---

## 7. Cloud Deployment (Render, Railway, Docker)

### 7.1 Multi-Stage Docker Build
The included `Dockerfile` uses a multi-stage process that automatically builds the React frontend in `node:20-slim` and mounts it into the Python runtime container:

```bash
# Build and run container locally
docker-compose up -d --build
```
Access the application at: `http://localhost:8000`

### 7.2 Deploying to Render
1. Create a new **Web Service** on [Render](https://render.com) and link your GitHub repository.
2. Select **Docker** environment (Render automatically detects the multi-stage `Dockerfile`).
3. Under **Environment Variables**, add:
   - `LOCAL_LLM_ENABLED` = `true`
   - `LOCAL_LLM_ENDPOINT` = `https://integrate.api.nvidia.com/v1`
   - `LOCAL_LLM_MODEL` = `nvidia/nemotron-3.5-super-vl-120b-a12b`
   - `CUSTOM_LLM_API_KEY` = `your_nvidia_nim_api_key_here`
4. Deploy. Render will compile the frontend, configure the backend, bind to the dynamic `$PORT`, and provide your live HTTPS URL.

---

## 8. Automated Test Suite

A comprehensive test suite verifies deterministic rules, ClaimGuard verification, the Reliability Principle, visual color calculations, intent-preserving rewriting, and API endpoints:

```powershell
# Run from repository root
$env:PYTHONPATH="d:\brd-ai\backend"; python -m pytest -p no:pytest_ethereum backend/tests -v
```

**Test Coverage (18 passing tests):**
- `test_rule_engine.py`: Prohibited terms, regex word boundary matching, score deductions.
- `test_claim_guard.py`: Verified fact matching, contradiction detection, and the Reliability Principle (`UNSUPPORTED_NEEDS_REVIEW`).
- `test_visual_inspector.py`: RGB/Hex conversions, color distance ($\Delta E$), and WCAG contrast ratio calculations.
- `test_rewriter.py`: Revision application and rejection handling.
- `test_semantic_engine.py`: Clause negation and disclaimer detection.
- `test_api.py`: Brand management, end-to-end submission, human review workflow, audit trail, settings, and Brand Drift analytics.

---

## 9. Project Directory Structure

```
d:\brd-ai\
├── backend/
│   ├── app/
│   │   ├── api/                     # FastAPI route controllers
│   │   │   ├── brands_router.py     # Brand profiles, rules, facts CRUD & guideline extraction
│   │   │   ├── submissions_router.py# Submissions and sanitized file uploads (PDF, DOCX, Image)
│   │   │   ├── review_router.py     # Human review workflow & final publication gate
│   │   │   ├── analytics_router.py  # Brand Drift aggregation & governance insights
│   │   │   ├── settings_router.py   # Runtime settings & LLM connectivity testing
│   │   │   └── chat_router.py       # Sentinel AI Copilot chatbot endpoint
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── brand.py             # BrandProfile, BrandRule, ApprovedFact
│   │   │   ├── submission.py        # ContentSubmission, AnalysisReport, IssueFinding
│   │   │   └── review.py            # HumanReviewAudit
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── services/                # Core business logic & algorithms
│   │   │   ├── extractor_service.py # PyMuPDF, python-docx, OCR text extraction
│   │   │   ├── rule_engine.py       # Deterministic word-boundary rule matching
│   │   │   ├── claim_guard.py       # ClaimGuard fact checking & Reliability Principle
│   │   │   ├── tone_inspector.py    # Voice adherence & avoided tone detection
│   │   │   ├── visual_inspector.py  # OpenCV K-Means color clustering & WCAG contrast
│   │   │   ├── gemini_service.py    # Tier 1: Google Gemini API connector & model cascade
│   │   │   ├── local_llm_service.py # Tier 2: NVIDIA NIM / Ollama OpenAI-compatible connector
│   │   │   ├── semantic_engine.py   # Tier 3: Context-aware semantic NLP (always available)
│   │   │   ├── inspection_service.py# Orchestrates 3-tier cascade inspection pipeline
│   │   │   ├── dynamic_guideline_parser.py # Extracts Brand DNA from any policy document
│   │   │   ├── rewriter_service.py  # Intent-preserving smart rewriting & diffs
│   │   │   ├── analytics_service.py # Brand drift metrics & gap recommendations
│   │   │   └── seed_service.py      # Pre-seeded demo brands and realistic submissions
│   │   ├── config.py                # Environment configuration & uploads path
│   │   ├── database.py              # SQLite engine & session management
│   │   └── main.py                  # App entrypoint, middleware, static SPA mounting
│   ├── tests/                       # Automated pytest suite (18 unit & integration tests)
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                 # Clean environment variable template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx           # Top navigation, brand switcher, engine status
│   │   │   ├── ContentSubmitter.jsx # Submission form with sample templates & file upload
│   │   │   ├── InspectionReport.jsx # Sub-nav view switcher & top action bar
│   │   │   ├── DocumentAISummary.jsx# Dedicated AI Summary & Executive Briefing Page
│   │   │   ├── DocumentReader.jsx   # Extracted document text reader with search & copy
│   │   │   ├── ClaimGuardPanel.jsx  # Factual claims ledger & proof citations
│   │   │   ├── VisualInspectorCard.jsx # Dominant palette extraction & contrast ratios
│   │   │   ├── HumanReviewModal.jsx # Revision accept/edit/reject modal & sign-off
│   │   │   ├── BrandDNAEditor.jsx   # Rules dictionary, facts, visual swatches, guideline importer
│   │   │   ├── BrandDriftDashboard.jsx # Recurring violations & governance gap insights
│   │   │   ├── HistoryList.jsx      # Audit history with single & bulk delete options
│   │   │   ├── SettingsModal.jsx    # LLM configuration & connection testing modal
│   │   │   └── BrandChatbot.jsx     # Floating Sentinel AI Copilot chatbot
│   │   ├── services/
│   │   │   └── api.js               # Clean async fetch client for all backend endpoints
│   │   ├── App.jsx                  # Root layout & view state manager
│   │   ├── index.css                # Tailwind styling & custom scrollbars
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── sample_documents/                # Pre-packaged sample PDFs, DOCX files, and images
├── Dockerfile                       # Multi-stage production container build
├── docker-compose.yml               # Multi-container orchestration configuration
├── start.bat                        # Windows Command Prompt launcher
├── start.ps1                        # Windows PowerShell launcher
└── README.md                        # Master platform documentation
```

---

## 10. Responsible AI & Enterprise Governance

- **Human Reviewers Retain Final Authority:** BrandSentinel AI acts as an advisor; authorized human reviewers retain control over accepting revisions and giving final publication clearance.
- **Evidence-Based Auditing:** Claims are evaluated against verified company records. Missing evidence results in an `UNSUPPORTED_NEEDS_REVIEW` designation rather than an unsubstantiated dismissal.
- **Confidentiality & Privacy:** Content and credentials are protected by server-side masking and zero-leakage security design.
