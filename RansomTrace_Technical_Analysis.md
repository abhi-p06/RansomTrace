# RansomTrace: Comprehensive Technical Analysis & Academic Fact-Base

**Document Type:** Technical Verification & Ground-Truth System Specification  
**Project Name:** RansomTrace  
**Full Title:** Cybercrime Investigation, Cryptocurrency Forensics & AI-Based Ransomware Payment Analysis Platform  
**Academic Context:** B.Tech Cybersecurity Course Capstone Project  
**Repository Location:** `/Users/abby/Desktop/cybersecproj`  
**Analysis Date:** October 2026  
**Target Consumer:** AI Assistant / Academic Report Writer for B.Tech Capstone Project Report Preparation  

---

## 📌 Executive Summary

This document presents a rigorous, ground-truth technical audit of the **RansomTrace** repository. Every claim, architecture diagram, mathematical formula, feature extraction method, database schema, API route, and digital forensics mechanism was audited directly against the active source code in `/Users/abby/Desktop/cybersecproj`. 

### Key Findings at a Glance
1. **Core Working Architecture:** The platform is a fully functional web-based Digital Forensics Incident Response (DFIR) and cryptocurrency investigation workbench. The backend is implemented in Python 3.13 / FastAPI with SQLAlchemy ORM (SQLite zero-configuration development database and PostgreSQL Docker container definition). The frontend is built on Next.js 16 (App Router), TypeScript, Tailwind CSS, Lucide icons, and D3.js force-directed graph visualization.
2. **Blockchain Data Ingestion & Dual-Mode Architecture:** Ingests live Bitcoin public ledger data via the external `mempool.space` REST API (with Base58Check and Bech32 address validation). It also includes an offline **Demonstration Mode** (`CASE-DEMO-SYNTHETIC-001` and `data/sample_cases/wannacry_sample.json`) providing zero-latency, rate-limit-immune demonstration capabilities for viva defense.
3. **Machine Learning Discrepancy (Claim vs. Reality):** The `README.md` claims "14 engineered UTXO behavioral heuristics (peel chains, velocity, fan-out)". The actual active backend implementation in `backend/app/services/ml_service.py` extracts strictly **7 behavioral features** (`transaction_count`, `average_transaction_amount`, `incoming_count`, `outgoing_count`, `unique_counterparties`, `transaction_frequency`, `amount_variance`). The model is an **Isolation Forest** from `scikit-learn` (`n_estimators=100`, `contamination=0.15`, `random_state=42`). Crucially, the model is **fit on-the-fly** during each analysis request using a 10-row hardcoded baseline matrix (`BASELINE_CORPUS`) stacked with the target vector; there is **no persistent trained model file** (`.pkl` or `.joblib`) stored on disk.
4. **Fund Flow Graph Scope:** While `backend/app/api/v1/graph.py` accepts depth query parameters up to 3, `backend/app/services/graph_service.py` explicitly restricts traversal to **Depth 1** (direct senders and direct recipients only) to maintain predictable execution and avoid recursive crawling.
5. **Digital Evidence & Legal Integrity:** The platform implements deterministic canonical JSON serialization (adhering to RFC 8785 principles with sorted keys and no whitespace) and generates cryptographic SHA-256 digests via Python `hashlib`. It implements an append-only, tamper-evident Chain of Custody ledger (`chain_of_custody_entries` table). Section 65B of the Indian IT Act / Indian Evidence Act and ISO/IEC 27037 are addressed via an **embedded statutory declaration within Section 13 of the generated ReportLab PDF**, rather than a standalone statutory Certificate Form 65B(4).
6. **Test Suite Status:** 80 automated test cases exist across 14 test modules in `backend/tests/`. Under Python 3.13, **54 tests pass and 26 tests fail**. The failures are primarily due to architectural refactoring where service interfaces were simplified (e.g., test expecting 12/14 features vs. the 7 implemented, tests expecting depth 2-3 graphs vs. depth 1 implementation, and a rate-limiter test failing because `testclient` is explicitly whitelisted from IP throttling).

---

## SECTION A: Project Overview

### 1. Purpose and Problem Statement
Ransomware syndicates extort billions of dollars globally by deploying cryptoworms to encrypt enterprise infrastructure and demanding ransom payments in Bitcoin. Once victims pay, extortionists rapidly launder funds across intermediary wallets, peeling chains, and mixer services.
Traditional digital forensics incident response (DFIR) teams and law enforcement agencies face critical bottlenecks:
* **Blockchain Complexity:** Raw hexadecimal transaction hashes, UTXO splitting, and change outputs are difficult to trace manually.
* **Rapid Dissipation:** Funds are dispersed within minutes of payment.
* **Evidentiary Inadmissibility:** Ad-hoc blockchain explorer screenshots do not meet the stringent legal standards required for court admissibility (e.g., Section 65B of the Indian Information Technology Act 2000 / Indian Evidence Act 1872, and ISO/IEC 27037).

**RansomTrace** solves this problem by providing an integrated cyber SOC platform combining Bitcoin ledger ingestion, topological fund-flow mapping, unsupervised statistical outlier detection, transparent multi-factor risk scoring, SHA-256 tamper-evident evidence preservation, and automated PDF forensic dossier generation.

### 2. Intended Users & Personas
* **DFIR Incident Responders:** Investigating ransomware outbreak notes, tracking ransom payments from victim treasury wallets.
* **Law Enforcement Cybercrime Units:** Generating court-admissible forensic dossiers and establishing fund exit points.
* **Cyber Insurance Forensic Assessors:** Verifying payment claims and tracking loss recovery.
* **Cybersecurity Students & Academics:** Demonstrating cryptocurrency forensic workflows, evidence custody, and applied unsupervised machine learning in a capstone environment.

### 3. Core Objectives & Operational Boundaries
| Objective | Status | Implementation Truth |
| :--- | :--- | :--- |
| Bitcoin Public Ledger Ingestion | `VERIFIED IN SOURCE` | Via `https://mempool.space/api` (`mempool_client.py:L80-179`). |
| Synthetic Offline Demo Mode | `VERIFIED IN SOURCE` | Preloaded multi-hop case `CASE-DEMO-SYNTHETIC-001` (`data_layer.py:L356-470`). |
| Behavioral Anomaly Detection | `VERIFIED IN SOURCE` | Scikit-learn `IsolationForest` over 7 features (`ml_service.py:L220-285`). |
| Hybrid Risk Prioritization | `VERIFIED IN SOURCE` | 5 transparent indicators totaling 100 points (`risk_service.py:L52-120`). |
| Evidence Vault & Chain of Custody | `VERIFIED IN SOURCE` | Canonical SHA-256 hashing & append-only DB ledger (`evidence_service.py:L54-255`). |
| Forensic PDF Report Generation | `VERIFIED IN SOURCE` | 13-section ReportLab PDF with embedded Section 65B clause (`report_service.py:L125-1250`). |
| Real-World Attacker Deanonymization | `NOT FOUND` / `OUT OF SCOPE` | Explicitly prohibited; Bitcoin addresses are pseudonymous. Does not harvest PII. |
| Fund Seizure / Private Key Handling | `NOT FOUND` / `OUT OF SCOPE` | Zero wallet custody; strictly read-only public ledger forensics. |

### 4. Main Functional Modules
1. **Module 1 (Case & Incident Lifecycle):** Docket creation, metadata tracking, severity triage (`Open`, `Investigating`, `Contained`, `Closed`), and alignment with NIST SP 800-61.
2. **Module 2 (Blockchain Ledger Ingestion):** Address validation (P2PKH, P2SH, Bech32, Taproot), transaction fetching, inputs/outputs normalization, and balance computation.
3. **Module 3 (Topological Fund Flow Engine):** Directed graph modeling (nodes = wallets, edges = transactions) with NetworkX and interactive D3 force simulations.
4. **Module 4 (Statistical Analytics Engine):** 10 standalone forensic metrics, daily transaction volume timelines, and counterparty value rankings.
5. **Module 5 (Machine Learning Anomaly Engine):** Isolation Forest unsupervised outlier scoring with human-readable behavioral explanations.
6. **Module 6 (Investigative Risk Scoring):** Weighted multi-factor risk calculation (0–100 scale: Low, Medium, High, Critical).
7. **Module 7 (Digital Evidence Vault & Chain of Custody):** ISO/IEC 27037 evidence preservation, RFC 8785 canonical JSON serialization, SHA-256 integrity verification, and append-only audit trail.
8. **Module 8 (Legal Reporting & Compliance):** 13-section PDF forensic report compilation with running headers, page totals, and Section 65B statutory disclaimer.

---

## SECTION B: Repository Structure

### 1. Directory Tree
```text
cybersecproj/
├── README.md                                  # Executive summary & syllabus mapping
├── RANSOMTRACE_COMPLETE_LEARNING_GUIDE.md    # 2035-line comprehensive viva & technical guide
├── docker-compose.yml                         # PostgreSQL 16 Alpine service definition
├── .env / .env.example                        # Platform environment configuration
├── database/                                  # Empty directory (reserved for future schema scripts)
├── modules/                                   # Empty directory (reserved for future microservices)
├── data/
│   ├── evidence_vault/                        # Filesystem evidence artifact directory
│   └── sample_cases/
│       └── wannacry_sample.json               # WannaCry May 2017 historical benchmark case
├── backend/
│   ├── requirements.txt                       # Backend Python dependencies
│   ├── alembic.ini                            # Alembic database migration configuration
│   ├── ransomtrace.db                         # SQLite active local database (1.3 MB)
│   ├── alembic/
│   │   ├── env.py                             # Alembic runtime environment
│   │   └── versions/
│   │       ├── 0ec8b489a4e1_initial_schema.py
│   │       ├── a52a80d48337_create_core_forensics_tables.py
│   │       ├── 02ff5e630272_update_ml_analysis_fields.py
│   │       └── bb2579ce6851_add_evidence_forensic_fields.py
│   ├── app/
│   │   ├── main.py                            # FastAPI application entry, CORS, & middlewares
│   │   ├── core/
│   │   │   ├── config.py                      # Pydantic BaseSettings & environment loading
│   │   │   ├── database.py                    # SQLAlchemy Engine, SessionLocal, & health check
│   │   │   └── security.py                    # RateLimiter, SecurityHeaders, regex sanitizers
│   │   ├── models/
│   │   │   ├── base.py                        # BaseModel with UUID primary key & timestamps
│   │   │   ├── case.py                        # InvestigationCase ORM model
│   │   │   ├── wallet.py                      # Wallet & WalletRelation ORM models
│   │   │   ├── transaction.py                 # Transaction ORM model with JSON I/O
│   │   │   ├── evidence.py                    # Evidence ORM model (SHA-256 sealed)
│   │   │   ├── custody.py                     # ChainOfCustodyEntry append-only model
│   │   │   └── analysis.py                    # RiskAssessment & MLAnalysis ORM models
│   │   ├── schemas/
│   │   │   ├── case.py, wallet.py, transaction.py
│   │   │   ├── analytics.py, graph.py, ml.py
│   │   │   ├── risk.py, evidence.py, report.py, dashboard.py
│   │   ├── services/
│   │   │   ├── data_layer.py                  # CRUD operations & synthetic demo dataset loader
│   │   │   ├── mempool_client.py              # Mempool API client & Bitcoin address validator
│   │   │   ├── blockchain_service.py          # Dual-mode ledger coordinator & TX normalizer
│   │   │   ├── analytics_service.py           # 10 core forensic metrics & time-series
│   │   │   ├── graph_service.py               # Depth-1 NetworkX directed graph engine
│   │   │   ├── ml_service.py                  # Isolation Forest 7-feature anomaly engine
│   │   │   ├── risk_service.py                # 5-factor 0-100 risk scoring engine
│   │   │   ├── evidence_service.py            # Canonical JSON, SHA-256 hashing & verification
│   │   │   ├── dashboard_service.py           # SOC overview aggregations & activity timelines
│   │   │   └── report_service.py              # ReportLab 13-section PDF compiler
│   │   └── api/v1/
│   │       ├── router.py                      # API v1 router aggregator
│   │       ├── health.py, cases.py, wallets.py
│   │       ├── analytics.py, graph.py, ml.py
│   │       ├── risk.py, evidence.py, reports.py, dashboard.py
│   └── tests/
│       ├── test_analytics.py, test_blockchain.py, test_cases.py
│       ├── test_chain_of_custody.py, test_dashboard.py, test_digital_evidence.py
│       ├── test_edge_cases.py, test_evidence.py, test_graph.py
│       ├── test_ml.py, test_report.py, test_risk.py, test_risk_scoring.py, test_security.py
└── frontend/
    ├── package.json                           # Next.js 16, React 19, Tailwind CSS dependencies
    ├── next.config.ts                         # Next.js App Router configuration
    ├── tsconfig.json                          # TypeScript configuration
    └── src/
        ├── lib/
        │   ├── types.ts                       # Complete TypeScript DTO interfaces
        │   └── api.ts                         # Centralized fetch client for backend endpoints
        ├── components/
        │   ├── layout/
        │   │   ├── SOCShell.tsx               # Main layout wrapper with header & sidebar
        │   │   ├── Header.tsx                 # System status bar & quick case switcher
        │   │   └── Sidebar.tsx                # Cyber SOC navigation menu
        │   └── dashboard/
        │       ├── SystemMetrics.tsx          # Summary KPI cards (active cases, BTC volume)
        │       ├── QuickActions.tsx           # Direct action shortcuts
        │       └── SyllabusRoadmap.tsx        # Academic syllabus module tracker
        └── app/
            ├── layout.tsx, globals.css, favicon.ico
            ├── page.tsx                       # SOC Command Center (Dashboard)
            ├── ingestion/page.tsx             # Public Bitcoin Wallet Search & Lookup
            ├── cases/page.tsx                 # Investigation Cases Docket List
            ├── cases/[id]/page.tsx            # Case Detail, Target Wallet, & Evidence Tab
            ├── graph/page.tsx                 # D3 Fund-Flow Force-Directed Visualizer
            ├── analytics/page.tsx             # 10 Core Forensic Metrics & Recharts Graphs
            ├── ai-analysis/page.tsx           # Redirect wrapper to /ml-risk
            ├── ml-risk/page.tsx               # ML Anomaly & Risk Breakdown Dashboard
            ├── risk/page.tsx                  # Dedicated Risk Scoring Engine UI
            ├── evidence/page.tsx              # Digital Evidence Locker & Tamper Verifier
            ├── custody/page.tsx               # Append-Only Chain of Custody Audit Log
            ├── reports/page.tsx               # PDF Report Previewer & Instant Download
            └── legal/page.tsx                 # Statutory Legal Frameworks & ISO/IT Act Reference
```

---

## SECTION C: Technology Stack and Architecture

### 1. Technology Inventory
| Component | Claimed Technology | Actual Verified Technology | Version | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Framework** | Next.js 14+ | Next.js (App Router, Turbopack) | `16.3.8` | `VERIFIED IN SOURCE` (`frontend/package.json:L15`) |
| **Frontend Runtime** | React | React | `19.2.8` | `VERIFIED IN SOURCE` (`frontend/package.json:L16`) |
| **Styling** | Tailwind CSS | Tailwind CSS (PostCSS plugin) | `^4.0.0` | `VERIFIED IN SOURCE` (`frontend/package.json:L27`) |
| **Iconography** | Lucide Icons | Lucide React | `^1.52.0` | `VERIFIED IN SOURCE` (`frontend/package.json:L14`) |
| **Graph Visualization** | D3.js | D3 (Force Simulation & Zoom) | `^7.9.0` | `VERIFIED IN SOURCE` (`frontend/package.json:L13`) |
| **Charting** | Recharts | Recharts | `^3.10.1` | `VERIFIED IN SOURCE` (`frontend/package.json:L18`) |
| **Backend Framework** | Python FastAPI | FastAPI | `>=0.110.0` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L1`) |
| **ASGI Web Server** | Uvicorn | Uvicorn (Standard with uvloop/httptools) | `>=0.28.0` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L2`) |
| **Python Version** | Python 3.11+ | Python 3.13 (Miniconda ARM64) | `3.13.13` | `VERIFIED BY TEST OR OUTPUT` |
| **ORM / Data Access** | SQLAlchemy 2.0 | SQLAlchemy | `>=2.0.28` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L5`) |
| **Database Engine** | SQLite / Postgres | SQLite (`ransomtrace.db`) & Postgres ready | SQLite 3 | `VERIFIED IN SOURCE` (`docker-compose.yml`, `config.py:L27`) |
| **Database Migrations**| Alembic | Alembic | `>=1.13.0` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L6`) |
| **Machine Learning** | scikit-learn | scikit-learn (`IsolationForest`) | `>=1.4.0` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L9`) |
| **Numerical Processing**| NumPy | NumPy | `>=1.26.0` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L10`) |
| **Network Graph Lib** | NetworkX | NetworkX (`DiGraph`) | `>=3.2.1` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L11`) |
| **PDF Generation** | ReportLab | ReportLab (`SimpleDocTemplate`, `canvas`) | `>=4.1.0` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L12`) |
| **HTTP Client** | HTTPX | HTTPX (AsyncClient) | `>=0.27.0` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L8`) |
| **Validation** | Pydantic v2 | Pydantic & Pydantic Settings | `>=2.6.0` | `VERIFIED IN SOURCE` (`backend/requirements.txt:L3-4`) |

### 2. Actual System Data Flow
```text
 +-----------------------------------------------------------------------------------------+
 |                                NEXT.JS FRONTEND (PORT 3000)                             |
 |  [Ingestion / Cases / D3 Graph / Recharts Analytics / ML Anomaly / Evidence Vault / PDF] |
 +-----------------------------------------------------------------------------------------+
                                           |  HTTP REST (JSON / PDF Stream)
                                           v
 +-----------------------------------------------------------------------------------------+
 |                                FASTAPI BACKEND (PORT 8000)                              |
 |  Middlewares: RequestSizeLimit (10MB) -> RateLimiter (2000/min) -> SecurityHeaders       |
 |  Router: /api/v1 (health, cases, wallets, analytics, graph, ml, risk, evidence, reports)  |
 +-----------------------------------------------------------------------------------------+
        |                                 |                             |
        | Dual-Mode Ingestion             | ML & Graph Engines          | Forensic Preservation
        v                                 v                             v
+-----------------------+     +-----------------------+     +-------------------------------+
|  BLOCKCHAIN SOURCES   |     | ANALYTICS & AI ENGINES|     |     EVIDENCE & AUDIT VAULT    |
| - Live: Mempool API   |     | - 10 Core Metrics     |     | - RFC 8785 Canonical JSON     |
|   (https://mempool.   |     | - NetworkX (Depth 1)  |     | - Python hashlib SHA-256      |
|    space/api)         |     | - Isolation Forest    |     | - Append-only Custody Ledger  |
| - Offline Demo Mode   |     |   (Fit on-the-fly)    |     | - ReportLab PDF Engine        |
|   (Synthetic &        |     | - 5-Factor Risk Score |     |   (Section 65B IT Act Clause) |
|    WannaCry Cases)    |     |   (0 - 100 Scale)     |     +-------------------------------+
+-----------------------+     +-----------------------+                     |
        |                                 |                                 |
        +---------------------------------+---------------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |       SQLALCHEMY ORM DATA LAYER       |
                      |  - SQLite (backend/ransomtrace.db)    |
                      |  - PostgreSQL (Docker Compose :5432)  |
                      |  - 8 Tables & Append-Only Tracing     |
                      +---------------------------------------+
```

### 3. Complete Backend API Route Inventory
| Route Path | Method | Purpose | Source File Reference |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Discovery endpoint returning platform name, version, and health link | `backend/app/main.py:L121` |
| `/health` | `GET` | Root alias for system and database connectivity status | `backend/app/main.py:L133` |
| `/api/v1/health` | `GET` | Detailed diagnostic health check with database latency | `backend/app/api/v1/health.py:L14` |
| `/api/v1/dashboard/summary` | `GET` | SOC summary: counts of cases, wallets, evidence, anomalies, timeline | `backend/app/api/v1/dashboard.py:L14` |
| `/api/v1/cases` | `GET` | Retrieve list of cases with optional status, severity, and search filter | `backend/app/api/v1/cases.py:L21` |
| `/api/v1/cases` | `POST` | Create a new forensic investigation docket | `backend/app/api/v1/cases.py:L39` |
| `/api/v1/cases/{case_id}` | `GET` | Retrieve single case by UUID or string case identifier | `backend/app/api/v1/cases.py:L58` |
| `/api/v1/cases/{case_id}` | `PUT` | Update case status, severity, description, or target label | `backend/app/api/v1/cases.py:L74` |
| `/api/v1/cases/{case_id}` | `DELETE` | Delete case and cascade delete all associated wallets and evidence | `backend/app/api/v1/cases.py:L96` |
| `/api/v1/cases/demo/load` | `POST` | Re-initialize the pre-loaded synthetic demonstration dataset | `backend/app/api/v1/cases.py:L114` |
| `/api/v1/wallets/{address}` | `GET` | Query public Bitcoin wallet stats (dual-mode: demo or live Mempool) | `backend/app/api/v1/wallets.py:L17` |
| `/api/v1/wallets/{address}/transactions` | `GET` | Retrieve normalized transaction list for an address (inputs/outputs) | `backend/app/api/v1/wallets.py:L41` |
| `/api/v1/transactions/{txid}` | `GET` | Retrieve single normalized Bitcoin transaction record | `backend/app/api/v1/wallets.py:L69` |
| `/api/v1/wallets/{address}/analytics` | `GET` | Calculate 10 core forensic metrics and volume-over-time points | `backend/app/api/v1/analytics.py:L18` |
| `/api/v1/wallets/{address}/graph` | `GET` | Construct directed NetworkX fund-flow graph (Depth 1) | `backend/app/api/v1/graph.py:L14` |
| `/api/v1/ml/analyze` | `POST` | Run Isolation Forest anomaly detection on transactions provided in body | `backend/app/api/v1/ml.py:L17` |
| `/api/v1/ml/analyze/{wallet_address}` | `POST` | Fetch wallet transactions and run Isolation Forest anomaly detection | `backend/app/api/v1/ml.py:L40` |
| `/api/v1/ml/history/{wallet_address}` | `GET` | Retrieve historical ML anomaly scoring records for a wallet | `backend/app/api/v1/ml.py:L82` |
| `/api/v1/ml/model-info` | `GET` | Returns model hyperparameters (n_estimators=100, contamination=0.15) | `backend/app/api/v1/ml.py:L99` |
| `/api/v1/risk/assess` | `POST` | Evaluate 5 transparent risk factors for body-supplied transactions | `backend/app/api/v1/risk.py:L21` |
| `/api/v1/risk/assess/{wallet_address}` | `POST` | Evaluate 5 transparent risk factors and persist assessment to DB | `backend/app/api/v1/risk.py:L44` |
| `/api/v1/risk/history/{wallet_address}` | `GET` | Retrieve historical risk assessments for a wallet | `backend/app/api/v1/risk.py:L88` |
| `/api/v1/risk/rules` | `GET` | Return statutory risk rules, scoring weights, and threshold definitions | `backend/app/api/v1/risk.py:L105` |
| `/api/v1/evidence/preserve-transaction` | `POST` | Fast-path preservation of a single transaction as sealed evidence | `backend/app/api/v1/evidence.py:L22` |
| `/api/v1/evidence` | `GET` | List preserved evidence records filtered by case_id or artifact_type | `backend/app/api/v1/evidence.py:L45` |
| `/api/v1/evidence` | `POST` | Preserve custom forensic artifact, calculate SHA-256, create custody | `backend/app/api/v1/evidence.py:L64` |
| `/api/v1/evidence/{evidence_id}` | `GET` | Retrieve single evidence record with full Chain of Custody trail | `backend/app/api/v1/evidence.py:L86` |
| `/api/v1/evidence/{evidence_id}/verify` | `GET` | Re-hash canonical payload and verify SHA-256 integrity match | `backend/app/api/v1/evidence.py:L106` |
| `/api/v1/evidence/{evidence_id}/custody` | `POST` | Append a new immutable custodial action (`TRANSFERRED`, `REVIEWED`, etc.) | `backend/app/api/v1/evidence.py:L133` |
| `/api/v1/evidence/{evidence_id}/custody` | `GET` | Retrieve chronological Chain of Custody ledger for an evidence item | `backend/app/api/v1/evidence.py:L161` |
| `/api/v1/cases/{case_id}/evidence` | `GET` | Convenience alias to fetch all evidence linked to a specific case | `backend/app/api/v1/evidence.py:L181` |
| `/api/v1/cases/{case_id}/report/preview` | `GET` | Preview case data, metrics, and evidence count before generating PDF | `backend/app/api/v1/reports.py:L14` |
| `/api/v1/cases/{case_id}/report/pdf` | `GET` | Compile and stream 13-section court-ready ReportLab PDF report | `backend/app/api/v1/reports.py:L43` |
| `/api/v1/reports/{case_id}/pdf` | `GET` | Alias endpoint to download case PDF report | `backend/app/api/v1/reports.py:L47` |

---

## SECTION D: Dataset and Data Sources

### 1. Data Source Inventory
The platform uses **three distinct data sources**:

| Dataset / Source Name | Format | Storage Location | Size / Row Count | Role in System | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Synthetic Multi-Hop Demo Case (`CASE-DEMO-SYNTHETIC-001`)** | In-code Python dicts & SQL records | `backend/app/services/data_layer.py:L356-470` | 1 Case, 2 Wallets, 2 Multi-Hop Transactions | Provides instant offline demonstration of 3-step laundering (Victim payment -> Peeling hop -> Cashout). | `VERIFIED IN SOURCE` |
| **WannaCry 2017 Benchmark Case (`RT-2017-WCRY-001`)** | JSON file | `data/sample_cases/wannacry_sample.json` | 155 lines (4.6 KB), 8 transactions | Historical extortion payment benchmark on address `13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94`. | `VERIFIED IN SOURCE` |
| **Public Bitcoin Blockchain (Mempool API)** | JSON over HTTPS | External REST (`https://mempool.space/api`) | Live dynamic query | Ingests real-time public ledger transactions for arbitrary user-entered Bitcoin addresses. | `VERIFIED IN SOURCE` |
| **Active SQLite Database** | SQLite 3 binary file | `backend/ransomtrace.db` | 1.38 MB (156 cases, 5 wallets, 7 transactions, 225 evidence items, 737 custody entries) | Primary persistence layer for investigations, evidence, and audit logs. | `VERIFIED BY TEST OR OUTPUT` |
| **Isolation Forest Baseline Corpus (`BASELINE_CORPUS`)** | 2D NumPy array | `backend/app/services/ml_service.py:L103-114` | 10 rows × 7 columns | Calibration matrix representing normal, low-variance wallet behavior. | `VERIFIED IN SOURCE` |

### 2. Isolation Forest Training & Inference Data Truth
* **Label Status:** **Unlabeled**. The Isolation Forest algorithm is unsupervised and does not use training labels (`y` is not used).
* **Dataset Size & Training Source:** The model does **NOT** train on a large public Kaggle or Elliptic dataset. It uses a **10-sample hardcoded synthetic baseline matrix** (`BASELINE_CORPUS`) concatenated with the single feature vector of the wallet currently being evaluated.
* **Storage Format:** There is **NO saved model file** (`.joblib`, `.pkl`, or `.onnx`). The model is initialized and fit in RAM on every HTTP request.

---

## SECTION E: Bitcoin Blockchain Investigation

### 1. Address Validation Logic
Implemented in `backend/app/services/mempool_client.py:L30-78` and `backend/app/core/security.py:L68-99`:
* **Demonstration Synthetic Addresses:** Addresses starting with `1Demo`, `3Demo`, or `bc1demo` are permitted for offline viva exam demonstrations.
* **Legacy P2PKH (Pay-to-PubKey-Hash):** Starts with `1`, length 26–35 characters. Validates Base58 character alphabet and executes **double-SHA256 checksum verification** (`hashlib.sha256(hashlib.sha256(payload).digest())[:4] == checksum`).
* **P2SH (Pay-to-Script-Hash):** Starts with `3`, validated with Base58Check.
* **Native SegWit (P2WPKH/P2WSH):** Starts with `bc1q`, regex `^bc1[a-z0-9]{39,59}$`.
* **Taproot (P2TR):** Starts with `bc1p`, regex `^bc1[a-z0-9]{39,59}$`.
* **Testnet Formats:** Supported (`m`, `n`, `2`, `tb1`).

### 2. Transaction Decomposition and Flow Direction
Implemented in `backend/app/services/blockchain_service.py:L54-134`:
For every raw Bitcoin transaction, inputs (`vin`) and outputs (`vout`) are parsed into `TxIO` models:
* `amount_btc = round(sats / 100_000_000, 8)`
* If the investigated target address appears only in inputs: **`flow_direction = "OUTGOING"`**, net value is negative.
* If the investigated target address appears only in outputs: **`flow_direction = "INCOMING"`**, net value is positive.
* If the target address appears in both inputs and outputs (self-transfer/change): **`flow_direction = "INTERNAL"`**, net value is `target_received_sats - target_spent_sats`.
* If the target address appears in neither: **`flow_direction = "TRANSIT"`**.

### 3. Graph Construction & Multi-Hop Traversal Reality
* **Library:** `networkx.DiGraph` (`backend/app/services/graph_service.py:L67`).
* **Traversal Depth Claim vs. Reality:**
  - `README.md` and API Swagger documentation claim "multi-hop counterparty wallet reconnaissance" and allow query parameter `depth: int = Query(1, ge=1, le=3)`.
  - **Actual Code Truth:** `graph_service.py:L6` explicitly enforces:
    > *"Core Principles: 1. NO recursive crawling or multi-depth traversals (Depth is strictly 1: direct neighbors only). 2. Uses ONLY transaction records already available for the current investigation."*
  - **Graph Elements:**
    - `Target Node` (Electric Cyan `#00e5ff`): Depth 0.
    - `Inflow Sender Nodes` (Emerald `#10b981`): Direct counterparty addresses sending BTC to the target.
    - `Outflow Recipient Nodes` (Crimson `#f43f5e`): Direct counterparty addresses receiving BTC from the target.
    - `Edges`: Direct transactions annotated with `txid`, `amount_sats`, `amount_btc`, `block_time`, `block_time_iso`, and `confirmed`.
* **Graph Topological Metrics Calculated:**
  - `total_nodes = len(nodes_list)`
  - `total_edges = len(edges_list)`
  - `density = round(total_edges / max(1, total_nodes), 3)`
  - `degree = G.degree(addr)` (number of connected transaction flows)
  - `hub_addresses = [clean_target]`

---

## SECTION F: Machine Learning and Anomaly Detection

### 1. Implementation Details
The machine learning component is implemented in `backend/app/services/ml_service.py:L220-300`:
* **Algorithm:** `sklearn.ensemble.IsolationForest`.
* **Algorithm Class:** Unsupervised Decision-Tree-based outlier detection.
* **Hyperparameters Configured:**
  - `n_estimators = 100` (Number of isolation trees in the ensemble)
  - `contamination = 0.15` (Expected proportion of outliers in the dataset)
  - `random_state = 42` (Fixed random seed for deterministic, repeatable results)
  - `max_samples = "auto"` (Default scikit-learn behavior)

### 2. Feature Engineering: Claimed 14 vs. Actual 7 Heuristics
The project `README.md` claims:
> *"14 engineered UTXO behavioral heuristics (peel chains, velocity, fan-out)."*

**Actual Code Truth (`backend/app/services/ml_service.py:L55-98` and `L117-189`):**  
There are **strictly 7 features** extracted and passed to the model:

| Index | Feature Key | Label | Formula / Calculation Method | Baseline Median |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `transaction_count` | Transaction Count | `float(len(txs))` | `5.0` |
| 2 | `average_transaction_amount` | Average Amount (BTC) | `round(sum(amounts) / len(amounts), 4)` | `0.05 BTC` |
| 3 | `incoming_count` | Incoming Transactions | `sum(1 for tx in txs if flow_direction == "INCOMING")` | `3.0` |
| 4 | `outgoing_count` | Outgoing Transactions | `sum(1 for tx in txs if flow_direction == "OUTGOING")` | `2.0` |
| 5 | `unique_counterparties` | Unique Counterparties | Count of distinct external addresses in inputs and outputs excluding target | `4.0` |
| 6 | `transaction_frequency` | Velocity (tx/day) | `total_tx / max(1.0, (max_timestamp - min_timestamp) / 86400.0)` | `0.5 tx/day` |
| 7 | `amount_variance` | Amount Variance (BTC) | `sum((x - mean)^2 for x in amounts) / len(amounts)` | `0.02 BTC` |

*Note on the remaining 7 claimed heuristics:* Peel chain ratio, fan-out ratio, unconfirmed transaction velocity, zero-change output ratio, and coinjoin mixing heuristics are discussed in theoretical documentation and partly in `test_ml.py`, but **they are not in the active feature extraction vector** in `ml_service.py`.

### 3. Baseline Corpus (Calibration Data)
Defined in `backend/app/services/ml_service.py:L103-114`:
```python
BASELINE_CORPUS = np.array([
    # [tx_count, avg_amt, in_count, out_count, counterparties, tx_freq, amt_var]
    [1.0,  0.02, 1.0, 0.0, 1.0, 0.1,  0.000],
    [2.0,  0.04, 2.0, 0.0, 2.0, 0.15, 0.001],
    [3.0,  0.05, 2.0, 1.0, 3.0, 0.2,  0.002],
    [4.0,  0.08, 3.0, 1.0, 4.0, 0.3,  0.004],
    [5.0,  0.06, 3.0, 2.0, 4.0, 0.35, 0.003],
    [6.0,  0.10, 4.0, 2.0, 5.0, 0.4,  0.008],
    [8.0,  0.07, 5.0, 3.0, 6.0, 0.5,  0.005],
    [10.0, 0.09, 7.0, 3.0, 8.0, 0.6,  0.006],
    [12.0, 0.12, 8.0, 4.0, 9.0, 0.7,  0.010],
    [15.0, 0.15, 10.0, 5.0, 11.0, 0.8, 0.015],
])
```

### 4. Scoring, Normalization & Classification Formula
Implemented in `backend/app/services/ml_service.py:L263-284`:
1. **Fit:** `clf.fit(np.vstack([BASELINE_CORPUS, feature_vector]))`
2. **Decision Function:** `raw_score = float(clf.decision_function(feature_vector)[0])`  
   *(In scikit-learn, negative raw scores indicate anomalous outliers, while positive scores indicate inlier behavior).*
3. **0–100 Forensic Normalization:**
   $$\text{normalized\_score} = \text{round}\left(\text{clip}\left(50.0 - (\text{raw\_score} \times 125.0), 5.0, 95.0\right), 1\right)$$
4. **Classification Thresholds:**
   * `normalized_score < 35.0` $\rightarrow$ **`NORMAL`** (`is_anomaly = False`)
   * `35.0 <= normalized_score < 55.0` $\rightarrow$ **`LOW ANOMALY`** (`is_anomaly = True`)
   * `55.0 <= normalized_score < 75.0` $\rightarrow$ **`MEDIUM ANOMALY`** (`is_anomaly = True`)
   * `normalized_score >= 75.0` $\rightarrow$ **`HIGH ANOMALY`** (`is_anomaly = True`)

### 5. Behavioral Explainability
Implemented in `backend/app/services/ml_service.py:L192-218`:  
The platform generates explainable natural language justifications by evaluating threshold breaches against baseline parameters:
* `transaction_frequency > 1.0 tx/day` $\rightarrow$ *"Unusually high transaction frequency was observed."*
* `amount_variance > 0.1 BTC` $\rightarrow$ *"Transaction amounts show higher-than-normal variation."*
* `unique_counterparties >= 4` $\rightarrow$ *"Multiple distinct counterparties were observed."*
* `average_transaction_amount > 1.0 BTC` $\rightarrow$ *"High average transaction amounts detected compared to baseline transfers."*
* `incoming_count > 0 and outgoing_count > 0 and abs(in - out) <= 1` $\rightarrow$ *"Direct deposit-to-withdrawal pass-through behavior was observed."*

### 6. Quantitative Evaluation Truth
* **Verified Benchmark Metrics:** The repository does **NOT** contain measured Precision, Recall, F1-Score, or ROC-AUC benchmarks against labeled ground-truth datasets.
* **Academic Disclosure:** Because the Isolation Forest is an unsupervised model operating on cold-start blockchain queries, traditional supervised evaluation metrics do not exist in the codebase. Any assertion of "98% accuracy" in a student report would be fabricated.

---

## SECTION G: Digital Forensics and Evidence Integrity

### 1. Evidence Preservation Workflow
Implemented in `backend/app/services/evidence_service.py:L54-255`:
1. **Canonical JSON Serialization (RFC 8785 adherence):**
   Keys are lexicographically sorted, whitespace stripped, ensuring identical byte outputs regardless of operating system or Python dictionary ordering:
   ```python
   canonical_dict = {
       "amount": round(float(amount), 8) if amount is not None else 0.0,
       "case_id": str(case_id or "").strip(),
       "source": str(source or "").strip(),
       "timestamp": str(timestamp or "").strip(),
       "transaction_id": str(transaction_id or "").strip().lower(),
       "wallet_address": str(wallet_address or "").strip(),
   }
   json.dumps(canonical_dict, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
   ```
2. **Cryptographic SHA-256 Digest:**
   `sha256_hash = hashlib.sha256(canonical_bytes).hexdigest()`
3. **Database Sealing:**
   Persisted into `evidences` table with `id` (UUID4), `artifact_type` (`TRANSACTION_SNAPSHOT`, `WALLET_FINDING`, `GRAPH_CLUSTER`, `ML_ANOMALY_RECORD`), `sha256_hash`, `captured_by`, `raw_payload`, and `seized_at`.

### 2. Chain of Custody Audit Trail
Implemented in `backend/app/services/evidence_service.py:L210-252` and `L520-565`:
Every preserved evidence record automatically generates **three initial immutable custody entries**:
* `COLLECTED` (Actor: `Forensic Investigator`, Action: Initial capture from source)
* `HASHED` (Actor: `Python hashlib Engine`, Action: SHA-256 fingerprint generation)
* `STORED` (Actor: `Evidence Vault Subsystem`, Action: Secure persistence)
Subsequent custodial touchpoints (`TRANSFERRED`, `ANALYZED`, `VERIFIED`, `REVIEWED`, `SEALED`, `PRESENTED_IN_COURT`) are appended to the `chain_of_custody_entries` table.
* **Tamper Prevention:** Past custody entries cannot be updated or deleted via the API.

### 3. Cryptographic Verification & Tamper Detection
Implemented in `backend/app/services/evidence_service.py:L258-285`:
The `GET /api/v1/evidence/{evidence_id}/verify` endpoint extracts the stored evidence fields, re-executes canonical byte formatting, computes `hashlib.sha256()`, and compares the recomputed digest to `stored_hash`:
* If matching: Returns **`INTEGRITY VERIFIED`** (`is_verified = True`).
* If any bit or character was altered: Returns **`INTEGRITY CHECK FAILED`** (`is_verified = False`).

---

## SECTION H: Cybercrime Lifecycle, Laws, and Privacy

### 1. Syllabus & Legal Standard Mapping (Modules 1 – 5)
| Course Module | Syllabus Topic | Repository Implementation Reality | Source File | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Module 1: Understanding Cyber Crime** | Categories, ransomware extortion, real-world cases | WannaCry case archive preloaded; incident classification in Case model | `wannacry_sample.json`, `case.py:L6` | `VERIFIED IN SOURCE` |
| **Module 2: Life Cycle of Cyber Crime** | Incident response lifecycle, reconnaissance, fund movement | Incident status tracker (`Open` $\rightarrow$ `Investigating` $\rightarrow$ `Contained` $\rightarrow$ `Closed`) aligning with NIST SP 800-61 | `case.py:L6-10`, `data_layer.py:L82` | `VERIFIED IN SOURCE` |
| **Module 3: Legal Perspectives** | Indian IT Act 2000 (Sec 65B), DPDP Act 2023, GDPR | Section 65B evidentiary clause embedded in PDF reports; public-ledger-only privacy architecture | `report_service.py:L1226`, `legal/page.tsx:L28` | `PARTIALLY IMPLEMENTED` (Clause embedded in PDF; no standalone 65B form) |
| **Module 4: Computer Forensics** | Digital evidence lifecycle, chain of custody, integrity preservation | ISO/IEC 27037 Evidence Locker; canonical JSON serialization; SHA-256 verification | `evidence_service.py:L54`, `evidence/page.tsx` | `VERIFIED IN SOURCE` |
| **Module 5: Role of AI in Cybersecurity** | Proactive defense, anomaly detection | Scikit-learn Isolation Forest unsupervised outlier detection on 7 behavioral features | `ml_service.py:L220-285`, `ml-risk/page.tsx` | `VERIFIED IN SOURCE` |

### 2. Privacy by Design & Safeguards
* **Zero Private Key Handling:** Does not store private keys, seed phrases, or wallet credentials.
* **Public Ledger Exclusively:** Only queries public Bitcoin blockchain ledger information via Mempool.
* **No PII Collection:** Does not collect, store, or scrape real-world names, physical addresses, or KYC credentials (complying with Indian DPDP Act 2023 and GDPR Article 5 data minimization principles).
* **Statutory Non-Attribution Disclaimers:** Every report, API response, and UI dashboard prominently displays:
  > *"The risk score and anomaly detection are investigative prioritization indicators and do not constitute proof of ransomware activity or legal guilt."*

---

## SECTION I: Database and Backend Architecture

### 1. Database Schema Specification (8 Tables)
The active database is SQLite (`backend/ransomtrace.db`) with Alembic versioning:

```sql
-- 1. Investigation Cases Docket
CREATE TABLE investigation_cases (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    incident_type VARCHAR(100) NOT NULL,
    description TEXT,
    target_label VARCHAR(255),
    severity VARCHAR(20) NOT NULL DEFAULT 'Medium',
    status VARCHAR(20) NOT NULL DEFAULT 'Open',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 2. Tracked Bitcoin Wallets
CREATE TABLE wallets (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES investigation_cases(id) ON DELETE CASCADE,
    address VARCHAR(128) NOT NULL,
    label VARCHAR(255),
    wallet_type VARCHAR(50),
    balance_sats BIGINT NOT NULL DEFAULT 0,
    total_received_sats BIGINT NOT NULL DEFAULT 0,
    total_sent_sats BIGINT NOT NULL DEFAULT 0,
    tx_count INTEGER NOT NULL DEFAULT 0,
    first_seen_timestamp BIGINT,
    last_seen_timestamp BIGINT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 3. Normalized Bitcoin Transactions
CREATE TABLE transactions (
    id VARCHAR(36) PRIMARY KEY,
    wallet_id VARCHAR(36) NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    txid VARCHAR(64) NOT NULL,
    wallet_address VARCHAR(128),
    sender VARCHAR(128),
    receiver VARCHAR(128),
    amount FLOAT DEFAULT 0.0,
    block_height INTEGER,
    block_time BIGINT,
    fee_sats BIGINT NOT NULL DEFAULT 0,
    size_bytes INTEGER,
    net_value_sats BIGINT NOT NULL DEFAULT 0,
    flow_direction VARCHAR(20) NOT NULL DEFAULT 'INCOMING',
    raw_inputs JSON,
    raw_outputs JSON,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 4. Multi-Hop Wallet Graph Relations (Schema defined, currently empty)
CREATE TABLE wallet_relations (
    id VARCHAR(36) PRIMARY KEY,
    source_wallet_id VARCHAR(36) NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    target_address VARCHAR(128) NOT NULL,
    txid VARCHAR(64) NOT NULL,
    value_sats BIGINT NOT NULL,
    relation_type VARCHAR(50) NOT NULL DEFAULT 'HOP',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 5. Digital Evidence Vault Artifacts
CREATE TABLE evidences (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES investigation_cases(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL,
    wallet_address VARCHAR(128),
    transaction_hash VARCHAR(128),
    amount_btc FLOAT,
    source VARCHAR(100) NOT NULL DEFAULT 'Public Bitcoin Blockchain / Mempool API',
    description TEXT,
    file_name VARCHAR(255),
    file_path VARCHAR(512),
    sha256_hash VARCHAR(64) NOT NULL,
    captured_by VARCHAR(100) NOT NULL,
    raw_payload JSON,
    seized_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 6. Append-Only Chain of Custody Ledger
CREATE TABLE chain_of_custody_entries (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES investigation_cases(id) ON DELETE CASCADE,
    evidence_id VARCHAR(36) REFERENCES evidences(id) ON DELETE SET NULL,
    action_performed VARCHAR(100) NOT NULL,
    actor_name VARCHAR(100) NOT NULL,
    notes TEXT,
    previous_hash VARCHAR(64),
    current_hash VARCHAR(64) NOT NULL,
    timestamp DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 7. Machine Learning Anomaly Detection History
CREATE TABLE ml_analyses (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) REFERENCES investigation_cases(id) ON DELETE CASCADE,
    wallet_id VARCHAR(36) REFERENCES wallets(id) ON DELETE SET NULL,
    wallet_address VARCHAR(128),
    model_name VARCHAR(100) NOT NULL DEFAULT 'IsolationForest',
    model_version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    raw_anomaly_score FLOAT NOT NULL,
    normalized_score FLOAT NOT NULL DEFAULT 0.0,
    classification VARCHAR(50) NOT NULL DEFAULT 'NORMAL',
    is_anomaly BOOLEAN NOT NULL DEFAULT 0,
    features_used JSON,
    feature_contributions JSON,
    explanation TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 8. Investigative Risk Assessments History
CREATE TABLE risk_assessments (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) REFERENCES investigation_cases(id) ON DELETE CASCADE,
    wallet_id VARCHAR(36) REFERENCES wallets(id) ON DELETE SET NULL,
    wallet_address VARCHAR(128),
    risk_score FLOAT NOT NULL,
    risk_tier VARCHAR(50) NOT NULL,
    heuristics_summary JSON,
    disclaimer TEXT NOT NULL,
    assessed_by VARCHAR(100) NOT NULL DEFAULT 'Automated Forensics Engine',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### 2. Alembic Migration History
* `0ec8b489a4e1_initial_schema.py` (Base migration)
* `a52a80d48337_create_core_forensics_tables.py` (Creates core tables: `investigation_cases`, `wallets`, `transactions`, `evidences`, `chain_of_custody_entries`)
* `02ff5e630272_update_ml_analysis_fields.py` (Adds `ml_analyses` and `risk_assessments`)
* `bb2579ce6851_add_evidence_forensic_fields.py` (Adds forensic audit fields to evidence records)

---

## SECTION J: Frontend and Application Workflow

### 1. User Interface Pages & Capabilities
| UI Route | File Path | Core Components & Controls | Backend API Calls |
| :--- | :--- | :--- | :--- |
| **SOC Dashboard** (`/`) | `frontend/src/app/page.tsx` | KPI cards, incident timeline, quick case launcher, syllabus roadmap | `GET /api/v1/dashboard/summary`, `GET /api/v1/health` |
| **Blockchain Ingestion** (`/ingestion`) | `frontend/src/app/ingestion/page.tsx` | Bitcoin address search input, format validator, balance cards, TX list | `GET /api/v1/wallets/{address}`, `GET /api/v1/wallets/{address}/transactions` |
| **Case Management** (`/cases`) | `frontend/src/app/cases/page.tsx` | Case docket table, status filter tabs, new case modal, demo loader button | `GET /api/v1/cases`, `POST /api/v1/cases`, `POST /api/v1/cases/demo/load` |
| **Case Detail** (`/cases/[id]`) | `frontend/src/app/cases/[id]/page.tsx` | Case metadata card, tracked wallets list, linked evidence table | `GET /api/v1/cases/{id}`, `GET /api/v1/cases/{id}/evidence` |
| **Fund-Flow Topology** (`/graph`) | `frontend/src/app/graph/page.tsx` | D3.js force-directed canvas, zoom controls, node inspector drawer | `GET /api/v1/wallets/{address}/graph` |
| **Behavioral Analytics** (`/analytics`) | `frontend/src/app/analytics/page.tsx` | 10 metrics KPI grid, Recharts volume bar chart, counterparty table | `GET /api/v1/wallets/{address}/analytics` |
| **AI Anomaly Detection** (`/ai-analysis` & `/ml-risk`) | `frontend/src/app/ml-risk/page.tsx` | Isolation Forest gauge, anomaly tier badge, behavioral explanation card | `POST /api/v1/ml/analyze/{address}`, `GET /api/v1/ml/history/{address}` |
| **Risk Scoring Engine** (`/risk`) | `frontend/src/app/risk/page.tsx` | 0-100 risk speedometer gauge, 5-indicator breakdown bar chart | `POST /api/v1/risk/assess/{address}`, `GET /api/v1/risk/rules` |
| **Evidence Vault** (`/evidence`) | `frontend/src/app/evidence/page.tsx` | Sealed evidence table, SHA-256 fingerprint display, instant verify button | `GET /api/v1/evidence`, `GET /api/v1/evidence/{id}/verify` |
| **Chain of Custody** (`/custody`) | `frontend/src/app/custody/page.tsx` | Chronological audit ledger, append custody action modal, actor tags | `GET /api/v1/evidence/{id}/custody`, `POST /api/v1/evidence/{id}/custody` |
| **Forensic PDF Reports** (`/reports`) | `frontend/src/app/reports/page.tsx` | Case report preview card, 13-section checklist, direct PDF download button | `GET /api/v1/cases/{id}/report/preview`, `GET /api/v1/cases/{id}/report/pdf` |
| **Legal Frameworks** (`/legal`) | `frontend/src/app/legal/page.tsx` | Educational guide to Section 65B IT Act 2000, ISO/IEC 27037, and DPDP Act | Static reference content |

### 2. End-to-End Investigation Walkthrough
1. **Case Inception:** The investigator opens `/cases` and clicks "New Case Docket" to create `CASE-2026-EXTORTION-01` (Severity: High, Status: Investigating).
2. **Wallet Search & Ledger Ingestion:** The investigator navigates to `/ingestion` and inputs the ransomware note payment address (e.g., `1DemoRansomCollectionWallet002`). The address format is validated as Legacy P2PKH; transactions and balance are ingested and cached into SQLite.
3. **Graph Topology Analysis:** Navigates to `/graph`. D3 renders the investigated wallet as an electric cyan hub with emerald sender nodes and crimson recipient nodes, revealing direct fund peeling.
4. **Statistical Analytics:** Navigates to `/analytics`. Inspects the 10 core metrics (e.g., transaction count, average amount, counterparty count, average time delta).
5. **Machine Learning Anomaly Detection:** Navigates to `/ml-risk`. Clicks "Run Isolation Forest Analysis". The backend extracts 7 features, scores them against `BASELINE_CORPUS`, returns `normalized_score: 56.8` (`MEDIUM ANOMALY`), and displays the behavioral explanation.
6. **Risk Assessment:** Clicks "Assess Risk". The 5-factor scoring engine calculates `32.2 / 100` (`MEDIUM`), breaking down contributions from frequency, variance, counterparties, velocity, and ML.
7. **Digital Evidence Sealing:** On the transaction table, clicks "Preserve as Evidence". The system formats the canonical RFC 8785 JSON representation, calculates the SHA-256 hash, creates the evidence record, and logs `COLLECTED`, `HASHED`, and `STORED` custody entries.
8. **Integrity Verification:** In `/evidence`, clicks "Verify Hash". The backend recalculates the SHA-256 digest and confirms `INTEGRITY VERIFIED`.
9. **PDF Forensic Dossier Export:** Navigates to `/reports` and clicks "Download Court-Ready PDF". The ReportLab engine compiles the 13 forensic sections, complete with case history, charts, SHA-256 manifest, and Section 65B IT Act certification clause.

---

## SECTION K: Results and Testing Evidence

### 1. Test Suite Execution Results (October 2026)
Executing `PYTHONPATH=. pytest backend/tests/` yields:
* **Total Tests Collected:** 80 tests across 14 test modules.
* **Passed:** **54 tests** (67.5%)
* **Failed:** **26 tests** (32.5%)
* **Warnings:** 4 Starlette deprecation warnings

#### Test Breakdown by Module
| Test Module | Tests | Passed | Failed | Root Cause of Failures |
| :--- | :--- | :--- | :--- | :--- |
| `test_cases.py` | 7 | 7 | 0 | All CRUD operations, validation, and demo reload passed. |
| `test_dashboard.py` | 5 | 5 | 0 | All KPI counts and recent activity queries passed. |
| `test_analytics.py` | 8 | 8 | 0 | All 10 individual metrics calculation functions passed. |
| `test_digital_evidence.py` | 6 | 6 | 0 | Canonical serialization and SHA-256 hashing passed. |
| `test_chain_of_custody.py` | 5 | 5 | 0 | Append-only custody creation and immutability passed. |
| `test_report.py` | 4 | 4 | 0 | ReportLab PDF compilation and 13 sections passed. |
| `test_risk_scoring.py` | 5 | 5 | 0 | Simple risk score calculation and weights passed. |
| `test_blockchain.py` | 5 | 3 | 2 | 2 tests failed due to live HTTP timeout / mock format mismatch. |
| `test_graph.py` | 5 | 3 | 2 | 2 tests failed because tests expected Depth 2 & 3, but service enforces Depth 1. |
| `test_ml.py` | 5 | 0 | 5 | Tests expected 12 features and class method `ml_service.extract_features()`; code refactored to module-level 7 features. |
| `test_risk.py` | 7 | 0 | 7 | Tests expected 7 rule contributions; active engine implements 4 rules + 1 ML. |
| `test_evidence.py` | 6 | 1 | 5 | API endpoint tests expected older payload schemas. |
| `test_edge_cases.py` | 6 | 2 | 4 | Unconfirmed TX and stress mocks had schema mismatches. |
| `test_security.py` | 6 | 5 | 1 | `test_rate_limiter_protection` failed because `testclient` is explicitly whitelisted from rate limiting in `security.py:L153`. |

---

## SECTION L: Limitations and Technical Issues

1. **Isolation Forest Feature Set Discrepancy:** The `README.md` claims 14 heuristics (peel chains, velocity, fan-out). The active model in `ml_service.py` uses strictly 7 features. Peel chain detection is not fed to the ML model.
2. **On-The-Fly Training vs. Pretrained Model:** The Isolation Forest is not trained on a historical corpus and saved to disk. It fits on-the-fly against a 10-sample synthetic baseline array on every single request.
3. **Graph Depth Limitation:** Although API query parameters allow `depth=1..3`, `graph_service.py` strictly restricts graph traversal to Depth 1 (direct neighbors only).
4. **Section 65B Implementation Format:** There is no separate standalone statutory Certificate Form 65B(4) (with system administrator affidavits, computer device identifiers, and hardware signatures). It is implemented as a standard legal text clause inside Section 13 of the PDF report.
5. **No Persistent Evidence File Vault:** While `data/evidence_vault/` exists, evidence payloads are currently stored entirely within the SQLite database `evidences.raw_payload` JSON column rather than as physical files written to disk.
6. **Whitelisted Rate-Limiter Bug:** `test_security.py:test_rate_limiter_protection` fails because `security.py:L153` hardcodes `"testclient"` in the exemption list, preventing the test client from triggering HTTP 429.
7. **External API Rate Limits:** Live queries rely on `mempool.space/api`. Without an enterprise API key, burst queries to high-volume addresses (like the Genesis block or exchange cold wallets) will encounter HTTP 429 rate limits.

---

## SECTION M: Academic Report Information Checklist

To assist another AI in preparing an academic project report for RansomTrace, use the following checklist:

### 1. Verified Core Project Information
* **Project Name:** RansomTrace
* **Subtitle:** Cybercrime Investigation, Cryptocurrency Forensics & AI-Based Ransomware Payment Analysis Platform
* **Academic Course:** B.Tech Computer Science / Cybersecurity Capstone Project
* **Architecture:** Decoupled Client-Server Micro-Architecture (Next.js 16 App Router + Python FastAPI 0.110 + SQLAlchemy 2.0 ORM + SQLite 3 / PostgreSQL 16)
* **Blockchain Target:** Bitcoin (BTC) Public Ledger via Mempool REST API (Mainnet & Testnet formats supported)

### 2. Exact Algorithmic Specifications
* **Machine Learning Model:** `scikit-learn` `IsolationForest`
  - Hyperparameters: `n_estimators=100`, `contamination=0.15`, `random_state=42`, `max_samples="auto"`
  - Features (7): `transaction_count`, `average_transaction_amount`, `incoming_count`, `outgoing_count`, `unique_counterparties`, `transaction_frequency`, `amount_variance`
  - Decision Thresholds: Normal ($<35$), Low Anomaly ($35-54$), Medium Anomaly ($55-74$), High Anomaly ($\ge 75$)
* **Risk Scoring Model:** 5-Factor Weighted Score (0–100 Points):
  - Frequency (20 pts), Amount Variation (15 pts), Counterparties (20 pts), Rapid Movement (20 pts), ML Anomaly Result (25 pts)
  - Tiers: Low ($0-29$), Medium ($30-59$), High ($60-79$), Critical ($80-100$)
* **Forensic Cryptography:** Deterministic RFC 8785 Canonical JSON byte serialization + Python `hashlib` SHA-256 hashing.

### 3. Missing Institutional & Student Details (Must Be Supplied Manually)
* **Student Name(s):** `[To be provided by user]`
* **Roll / Registration Number(s):** `[To be provided by user]`
* **Department / Faculty:** Department of Computer Science & Engineering / Information Security
* **University / Institution Name:** `[To be provided by user]`
* **Project Supervisor / Guide Name & Designation:** `[To be provided by user]`
* **Academic Submission Year / Semester:** 8th Semester / Final Year B.Tech (Academic Year 2025–2026 / 2026–2027)

### 4. Screenshots to Capture from the Running Project
Because the project is currently operational on `http://localhost:3000` (Frontend) and `http://127.0.0.1:8000` (Backend), the following real screenshots should be captured for the final report:
1. **SOC Command Center (`/`):** Showing KPI metrics (active cases, tracked wallets, evidence count, and activity timeline).
2. **Blockchain Ingestion & Wallet Search (`/ingestion`):** Showing input validation on `1DemoRansomCollectionWallet002` and ingested transactions.
3. **Directed Fund-Flow Topology (`/graph`):** Showing D3 force-directed graph with cyan target, green senders, and red recipients.
4. **Behavioral Analytics Dashboard (`/analytics`):** Showing the 10 core metrics cards, transaction volume bar chart, and counterparty value table.
5. **AI Anomaly Detection & Risk Engine (`/ml-risk` & `/risk`):** Showing Isolation Forest anomaly score gauge, explanation card, and 5-factor risk breakdown chart.
6. **Digital Evidence Vault (`/evidence`):** Showing SHA-256 fingerprint table and "INTEGRITY VERIFIED" badge modal.
7. **Chain of Custody Ledger (`/custody`):** Showing the append-only audit trail (`COLLECTED`, `HASHED`, `STORED`).
8. **Forensic PDF Report (`/reports`):** Showing preview screen and the downloaded 13-section PDF dossier with running header and Section 65B IT Act clause.
9. **Interactive Swagger API Documentation (`http://127.0.0.1:8000/docs`):** Showing FastAPI endpoint discovery.

---

## Unresolved Questions & Next Steps for the User
1. **Student & College Details:** Provide your name, roll number, college name, guide name, and submission date so the writing AI can fill out certificates and title pages.
2. **14 vs. 7 Features in Viva:** Decide whether your academic report should document the 7 active features implemented in code, or describe the 14 features as an extended proposed architecture with 7 implemented in the prototype. (Recommending: Document the 7 implemented in the prototype and describe the remaining 7 as Phase 2 extensions to maintain technical integrity during viva defense).
3. **Screenshot Collection:** Capture the screenshots listed in Section M from your browser while both local servers are running.
