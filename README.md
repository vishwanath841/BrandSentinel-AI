# BrandSentinel AI
### Intelligent Brand Governance & Content Compliance Platform
**CodeFrontier Hackathon Round 2 — Solo Developer: Vishwanath S A (GM Institute of Technology)**

> **Core Promise:** *Every piece of content should sound, look, and feel like the same brand.*

---

## 1. Overview & Problem Statement

Organizations publish content through dozens of employees, external agencies, and generative AI tools. Without centralized governance, creators inadvertently introduce:
- **Inconsistent Tone & Voice:** Aggressive, informal, or off-brand messaging.
- **Forbidden & Outdated Terminology:** Deprecated product names or buzzwords.
- **Unsupported Promotional Claims:** Exaggerated superlatives or metrics not verified by legal/product teams.
- **Visual Drift:** Deviations from approved brand colors, logo misuse, and low-contrast typography failing accessibility standards.

**BrandSentinel AI** is a real-time, pre-publication brand governance platform that reviews text, documents (PDF, Word DOCX), and images against an organization's approved brand identity. It explains detected issues, links findings to relevant brand rules with clear evidence, suggests intent-preserving revisions, and keeps authorized human reviewers in control of final publication.

---

## 2. Technology Stack & Lightweight Architecture

Engineered to run seamlessly on a standard 8GB RAM machine with low footprint and high responsiveness:

| Layer | Technology | Responsibility |
|---|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons | Responsive governance dashboard, review workspace, live preview, diffs |
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy | REST API, async workflow dispatch, file ingestion, rule engine |
| **Database** | SQLite | Lightweight zero-config database for brand profiles, rules, submissions, audit logs |
| **AI Analysis** | Google Gemini API, Local LLM (Ollama), Semantic NLP Engine | 3-Tier cascade: Gemini Cloud → Local LLM → Built-in Semantic Engine |
| **Deterministic Engine** | Python Regex & Boundary Parsers | Instant, zero-latency detection of forbidden terminology and competitor attacks |
| **Document Processing** | PyMuPDF (`fitz`), `python-docx` | High-fidelity extraction from PDF pages and Word documents |
| **Image Processing** | OpenCV (`cv2`), NumPy, PIL, OCR | K-Means dominant color extraction, $\Delta E$ Euclidean distance, WCAG 4.5:1 contrast |

---

## 3. Core Features & Round 2 Deliverables

### 3.1 Brand DNA Engine & Guideline Extraction
- **Multi-Brand Support:** Switch between brands (e.g. *ApexCloud Enterprise*, *EcoPulse Organics*, or create custom brands for agency clients).
- **Voice & Tone Configuration:** Specify approved voice traits (Authoritative, Data-driven, Empathetic) and avoided tones (Aggressive, Hyperbolic, Slang).
- **Rule Dictionary:** Configure preferred terminology vs prohibited phrases, with severity (Critical, High, Medium, Low) and educational rationales.
- **Visual Identity:** Manage primary, secondary, accent, background, and text hex colors with configurable color match tolerance ($\Delta E$).
- **Automated Guideline Ingestion:** Upload brand guideline PDFs or DOCX files; BrandSentinel extracts colors, rules, and facts into structured Brand DNA.

### 3.2 Content Submission & Multimodal Extraction
- **Text Editor:** Paste or write promotional copy, social posts, or blog drafts.
- **Document Processing:** Ingests `.pdf` via PyMuPDF and `.docx` via `python-docx` preserving structure.
- **Visual Assets:** Ingests `.png`, `.jpg`, `.jpeg`, `.webp` images.
- **1-Click Hackathon Sample Templates:** Load pre-configured sample submissions with intentional violations for instant evaluation.

### 3.3 ClaimGuard (Approved Fact & Claim Checking)
- **Strict Proposal Reliability Principle:**
  > *"The system distinguishes verified violations from uncertain findings. It will not claim a promotional statement is false solely because supporting evidence was not found; it will label it as unsupported or requiring review."*
- **Claim Classifications:**
  - `VERIFIED`: Exact or strong supporting evidence in approved brand facts.
  - `CONTRADICTION`: Claim directly contradicts approved facts (e.g. text claims "99.999% SLA" when approved SLA is "99.99%").
  - `UNSUPPORTED_NEEDS_REVIEW`: High-impact promotional claims or superlatives lacking proof in brand documentation. Labeled clearly as requiring human reviewer sign-off.
  - `COMPLIANT`: Factual statements adhering to guidelines.

### 3.4 Visual Brand Inspector (OpenCV)
- **Dominant Color Extraction:** Uses OpenCV K-Means color clustering to identify top 5 color clusters.
- **Palette Distance ($\Delta E$):** Computes Euclidean color distance to the nearest approved brand color and calculates the percentage of compliant pixels.
- **Accessibility Check:** Evaluates WCAG contrast ratio between dominant foreground and background colors (flags elements below 3.0:1 / 4.5:1).
- **Resolution Verification:** Flags low-resolution assets that risk pixelation on high-DPI displays.

### 3.5 Intent-Preserving AI Rewriter
- Generates smart suggestions that fix tone, terminology, or claim issues **while strictly preserving the creator's intended meaning, context, and value proposition**.
- Provides before/after diffs and explanatory rationales.

### 3.6 Human Review & Approval Workflow
- Authorised reviewers can interactively:
  - **Accept** a suggested revision (automatically updates document text).
  - **Edit** a suggestion inline to fine-tune phrasing.
  - **Reject** a suggestion with review notes.
- **Final Publication Gate:** Renders formal decision (`APPROVED`, `CHANGES_REQUESTED`, `REJECTED`) with reviewer identity and immutable audit log.

### 3.7 Brand Drift Analytics & Governance Insights
- Aggregates compliance scores and recurring violations across submissions.
- **Top Recurring Violations:** Pinpoints terminology creators repeatedly misuse.
- **Claim Hotspots:** Identifies topics where marketing makes claims lacking approved documentation.
- **Guideline Gap Recommendations:** Proactively advises brand managers where team documentation needs clarification.

---

## 4. Setup & Running Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 4.1 Quick Start (Production Full-Stack Mode)
FastAPI can serve both the backend API and the compiled React frontend simultaneously:

1. **Install Backend Dependencies:**
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

2. **Build Frontend:**
   ```powershell
   cd ../frontend
   npm install
   npm run build
   ```

3. **Start BrandSentinel AI Server:**
   ```powershell
   cd ../backend
   python -m uvicorn app.main:app --port 8000
   ```
   Open your browser to: **`http://localhost:8000`**

### 4.2 Docker Deployment (Single Command)
Per Section 6 of the proposal, BrandSentinel AI can be packaged and deployed consistently via Docker:

```powershell
# Build and run with Docker Compose
docker compose up --build -d
```
Open your browser to: **`http://localhost:8000`**

---

### 4.2 Development Mode (Hot Reloading)

If modifying frontend components and backend routes concurrently:

**Terminal 1 (Backend API):**
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend Vite Server):**
```powershell
cd frontend
npm run dev
```
Open your browser to: **`http://localhost:5173`** (API requests are automatically proxied to port 8000).

---

## 5. AI Engine Configuration (3-Tier Resilient Architecture)

BrandSentinel AI uses a **3-tier cascade** that guarantees the app always works, even without any API key or LLM server:

| Tier | Engine | When It's Used |
|------|--------|----------------|
| **1** | **Gemini Cloud API** | If `GEMINI_API_KEY` is configured and the API responds |
| **2** | **Local LLM (Ollama / LM Studio)** | If Tier 1 fails/unavailable and `LOCAL_LLM_ENABLED=true` with a reachable local server |
| **3** | **Built-in Semantic Engine** | Always available — zero dependencies, zero API keys needed |

### 5.1 Gemini API (Tier 1)
Configure via the Settings UI (gear icon) or `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 5.2 Local LLM — Ollama (Tier 2)
Use your own local model for development. After deployment, if the local LLM server isn't running, the app automatically falls back to Tier 3.

1. **Install Ollama:** https://ollama.com/download
2. **Pull a model:**
   ```bash
   ollama pull llama3.2
   ```
3. **Configure BrandSentinel** (`.env` or Settings UI):
   ```env
   LOCAL_LLM_ENABLED=true
   LOCAL_LLM_ENDPOINT=http://localhost:11434/v1
   LOCAL_LLM_MODEL=llama3.2
   ```
4. The Settings UI shows a live **Online/Offline** indicator and a **Test Local LLM** button.

### 5.3 Built-in Semantic Engine (Tier 3 — Always Available)
The Context-Aware Semantic NLP Engine runs locally with **zero external dependencies**:
- Deterministic rule matching with word-boundary precision
- ClaimGuard fact verification with the Reliability Principle
- Tone & voice adherence inspection
- Visual brand color validation (OpenCV)
- Clause negation & disclaimer detection

> **For evaluators:** After deployment, even if no Gemini key is set and no Ollama server is running, the full inspection pipeline works autonomously via Tier 3.

---

## 6. Running Automated Tests

A comprehensive automated test suite covers the deterministic rule engine, ClaimGuard verification, the Reliability Principle, visual color calculations, intent-preserving rewriting, and API endpoints:

```powershell
# Run from repository root
python -m pytest -o pythonpath=backend backend/tests -v
```

**Test Coverage Summary:**
- `test_rule_engine.py`: Prohibited terms, word boundary matching, score deductions.
- `test_claim_guard.py`: Verified fact matching, contradiction detection, and the Reliability Principle (`UNSUPPORTED_NEEDS_REVIEW`).
- `test_visual_inspector.py`: RGB/Hex conversions, color distance ($\Delta E$), WCAG contrast ratio calculations.
- `test_rewriter.py`: Revisions application and rejection handling.
- `test_api.py`: Brand management, end-to-end submission, human review workflow, audit trail, settings, and Brand Drift analytics.

---

## 7. Project Structure

```
d:\brd-ai\
├── backend/
│   ├── app/
│   │   ├── api/                     # FastAPI route controllers
│   │   │   ├── brands_router.py     # Brand profiles, rules, facts CRUD & guideline extraction
│   │   │   ├── submissions_router.py# Submissions and file uploads (PDF, DOCX, Image)
│   │   │   ├── review_router.py     # Human review and final approval gate
│   │   │   ├── analytics_router.py  # Brand Drift aggregation & governance insights
│   │   │   └── settings_router.py   # Runtime settings & Gemini connectivity
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── brand.py             # BrandProfile, BrandRule, ApprovedFact
│   │   │   ├── submission.py        # ContentSubmission, AnalysisReport, IssueFinding
│   │   │   └── review.py            # HumanReviewAudit
│   │   ├── schemas/                 # Pydantic schemas
│   │   ├── services/                # Core business logic & algorithms
│   │   │   ├── extractor_service.py # PyMuPDF, python-docx, OCR text extraction
│   │   │   ├── rule_engine.py       # Deterministic word-boundary rule matching
│   │   │   ├── claim_guard.py       # ClaimGuard fact checking & Reliability Principle
│   │   │   ├── tone_inspector.py    # Voice adherence & avoided tone detection
│   │   │   ├── visual_inspector.py  # OpenCV K-Means color clustering & WCAG contrast
│   │   │   ├── gemini_service.py    # Tier 1: Google Gemini API connector & model cascade
│   │   │   ├── local_llm_service.py # Tier 2: Local LLM (Ollama/LM Studio) OpenAI-compatible
│   │   │   ├── semantic_engine.py   # Tier 3: Context-aware semantic NLP (always available)
│   │   │   ├── inspection_service.py# Orchestrates 3-tier cascade inspection pipeline
│   │   │   ├── dynamic_guideline_parser.py # Extracts Brand DNA from any policy document
│   │   │   ├── rewriter_service.py  # Intent-preserving smart rewriting & diffs
│   │   │   ├── analytics_service.py # Brand drift metrics & gap recommendations
│   │   │   └── seed_service.py      # Pre-seeded demo brands and realistic submissions
│   │   ├── config.py                # Environment configuration & uploads path
│   │   ├── database.py              # SQLite engine & session management
│   │   └── main.py                  # App entrypoint, middleware, static SPA mounting
│   ├── tests/                       # Automated pytest suite
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                 # Example environment variables
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx           # Top navigation, brand switcher, engine status
│   │   │   ├── ContentSubmitter.jsx # Submission form with 1-click test templates
│   │   │   ├── InspectionReport.jsx # Executive score gauge, meters & findings list
│   │   │   ├── ClaimGuardPanel.jsx  # Fact verification & unsupported claim review
│   │   │   ├── VisualInspectorCard.jsx # OpenCV dominant color palette & contrast
│   │   │   ├── HumanReviewModal.jsx # Accept, edit, reject revisions & final sign-off
│   │   │   ├── BrandDNAEditor.jsx   # Rules dictionary, facts, visual swatches, importer
│   │   │   ├── BrandDriftDashboard.jsx # Recurring violations & governance insights
│   │   │   ├── HistoryList.jsx      # Submission history & audit trail
│   │   │   └── SettingsModal.jsx    # Gemini key configuration & connectivity testing
│   │   ├── services/
│   │   │   └── api.js               # Clean async fetch client for all backend endpoints
│   │   ├── App.jsx                  # Root layout & state manager
│   │   ├── index.css                # Tailwind styling & custom scrollbars
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── README.md
```

---

## 8. Responsible Design & Human Oversight

Aligned with Section 10 of the proposal:
- **Human Reviewers Retain Final Authority:** BrandSentinel AI acts as an advisor; authorized human reviewers retain full control over accepting revisions and approving publications.
- **No Fabricated Evidence:** Claims are strictly linked to verified company records. Missing evidence results in an `UNSUPPORTED_NEEDS_REVIEW` flag rather than a false refutation.
- **Privacy & Security:** Content is processed securely with zero external disclosure unless configured with approved Gemini API keys.

