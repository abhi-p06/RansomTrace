# RansomTrace: The Complete Technical Learning Guide & Viva Handbook
*A Comprehensive, Zero-Prerequisite Master Reference for Students and AI Tutors*  
*Documenting the Real, Working Implementation of the RansomTrace Platform*

---

## 📋 PREFACE & HOW TO USE THIS GUIDE

This document is a **pedagogical learning guide** and **viva defense handbook** for **RansomTrace**, an undergraduate cybercrime investigation, cryptocurrency forensics, and AI-assisted ransomware payment analysis platform.

### Target Audience
* **Beginner Students:** Undergraduate students with introductory knowledge of computer science, preparing for project vivas, lab examinations, and demonstrations.
* **AI Tutors & Mentors:** An AI assistant or teacher instructing students from absolute zero, walking them through code, theory, forensics, legal principles, and viva defense.

### Core Philosophy: Absolute Truth to the Codebase
Every technical fact, formula, technology, database table, API route, and machine learning parameter in this guide is taken directly from the **active, working codebase**.
* Nothing is invented.
* Features marked as planned or external are explicitly labeled.
* Real Python and TypeScript modules, file paths, and function signatures are referenced throughout.

---

# PART 1 — PROJECT OVERVIEW

### 1. What is RansomTrace?
**RansomTrace** is an open-source, web-based digital forensics and cryptocurrency investigation workbench. It enables cybercrime investigators, incident responders, and students to trace, inspect, statistically analyze, and document extortion fund movements on the public Bitcoin blockchain following a ransomware attack.

### 2. What problem does it solve?
When a corporate network or hospital is attacked by ransomware, the extortionists encrypt victim files and leave a ransom note demanding payment in cryptocurrency (typically Bitcoin) to a specific wallet address.

Historically, organizations and law enforcement faced severe challenges:
1. **Confusion over Blockchain Mechanics:** Investigators struggled to understand public ledger transactions, Satoshis, inputs, outputs, and unspent transaction outputs (UTXOs).
2. **Obfuscation & Fund Movement:** Attackers split payments across multiple intermediary addresses (peeling chains, hops, and mixers) within minutes of receiving payment.
3. **Manual Analysis Fatigue:** Examining hundreds of raw hexadecimal transaction IDs by hand is slow, error-prone, and inefficient.
4. **Failure to Maintain Court-Admissible Evidence:** Forensic evidence gathered haphazardly from public block explorers lacks cryptographic tamper-verification, chain-of-custody tracking, and legal compliance (e.g., Section 65B of the Indian Evidence Act / IT Act 2000).

**RansomTrace solves this** by providing an end-to-end investigation pipeline: from entering an extortion wallet address, pulling and normalizing transactions, generating directed fund-flow graphs, running unsupervised machine learning anomaly detection, calculating transparent risk scores, preserving immutable evidence with SHA-256 hashes, to compiling court-ready PDF forensic dossiers.

### 3. Why is ransomware relevant to cybersecurity?
Ransomware is malicious software (malware) that denies access to a computer system or data, typically through strong asymmetric/symmetric encryption, until a ransom is paid. It represents the single most economically devastating cybercrime threat globally:
* Attacks strike critical infrastructure (hospitals, power grids, government registries, educational institutions).
* Beyond data loss, victims suffer crippling operational downtime, regulatory penalties, and reputational collapse.
* Ransomware-as-a-Service (RaaS) models allow low-skilled criminals to rent sophisticated encryption payloads, scaling extortion operations worldwide.

### 4. Why is cryptocurrency used in ransomware payments?
Traditional electronic banking (wire transfers, credit cards, PayPal) requires **Know Your Customer (KYC)** compliance and centralized banking authorities. If an extortionist asks a victim to wire $100,000 to an international bank account, law enforcement can request an immediate asset freeze, reverse the transaction, and seize the account holder's identity documents.

Cryptocurrencies provide:
* **Pseudonymity:** Wallet addresses are alphanumeric cryptographic hashes with no names, email addresses, or physical locations attached.
* **Decentralization & Borderless Execution:** No government, central bank, or company controls the Bitcoin ledger. Transactions execute globally 24/7 without geographical or jurisdictional hurdles.
* **Irreversibility:** Once a Bitcoin block is mined and confirmed, transactions cannot be cancelled, charged back, or forcibly refunded.

### 5. Why is Bitcoin relevant to this project?
Bitcoin (BTC) was created in 2008 by Satoshi Nakamoto as the world's first decentralized peer-to-peer cryptocurrency.
1. **Most Prevalent Ransom Asset:** While privacy coins (like Monero) exist, Bitcoin remains the dominant cryptocurrency demanded by ransomware syndicates (WannaCry, LockBit, Conti, Ryuk, DarkSide) due to its vast global liquidity and the ease with which victims can purchase it through regulated exchanges.
2. **Fully Public, Transparent Ledger:** Every single Bitcoin transaction since Block 0 (the Genesis Block in January 2009) is recorded on an immutable, public database. Anyone in the world can inspect the flow of funds. This transparency makes Bitcoin the ideal target for digital forensics and academic investigation.

### 6. What exactly does our application do?
* **Ingests Public Blockchain Data:** Queries the public Mempool API to pull balances, transactions, timestamps, inputs, and outputs for any Bitcoin address.
* **Provides an Offline Demonstration Mode:** Includes synthetic preloaded cases (e.g., WannaCry benchmark and simulated multi-hop laundering) so investigations work seamlessly even without internet connectivity or when external APIs are rate-limited.
* **Calculates 10 Core Forensic Metrics:** Automatically computes transaction counts, inflows, outflows, average amounts, counterparties, velocity, and time deltas.
* **Builds Directed Fund-Flow Graphs:** Models wallets as nodes and transactions as edges using NetworkX, displaying direct inflow senders and outflow recipients.
* **Performs Unsupervised Anomaly Detection:** Applies scikit-learn's Isolation Forest model across 7 engineered behavioral features to detect unusual transaction patterns.
* **Calculates a 0–100 Investigative Risk Score:** Evaluates 5 transparent indicators (frequency, variance, counterparties, rapid movement, and ML anomaly score) to categorize investigation urgency.
* **Preserves Digital Evidence:** Converts transaction findings into canonical JSON structures and generates SHA-256 cryptographic hashes.
* **Enforces an Append-Only Chain of Custody:** Tracks every custodial touchpoint (`COLLECTED`, `HASHED`, `STORED`, `VERIFIED`, `REVIEWED`) and strictly forbids editing past logs.
* **Generates Court-Ready PDF Reports:** Compiles a complete investigation dossier using ReportLab, complete with case summaries, charts, hash manifests, and a Section 65B IT Act Certificate.

### 7. What does our application NOT do?
To maintain strict ethical, legal, and academic integrity, students must understand RansomTrace's limitations:
* ❌ It does **NOT** de-anonymize individuals or identify real-world owners of Bitcoin wallets (Bitcoin addresses are pseudonymous; linking a wallet to a human requires subpoenas to KYC-regulated cryptocurrency exchanges).
* ❌ It does **NOT** freeze, seize, or interact with cryptocurrency funds (it possesses zero private keys, wallet software, or fund transmission capabilities).
* ❌ It does **NOT** claim or prove criminal guilt (anomaly detection and risk scores are probabilistic investigative prioritization tools, not verdicts).
* ❌ It does **NOT** crack ransomware encryption (decrypting encrypted files requires private decryption keys or finding cryptographic implementation flaws in the malware binary).

### 8. Who would theoretically use such a system?
* **Digital Forensics Incident Response (DFIR) Teams:** Corporate incident responders analyzing payment instructions left on encrypted servers.
* **Law Enforcement Cybercrime Units:** Police cyber cells tracing illicit proceeds to identify exit points and crypto exchange cashouts.
* **Cyber Insurance Forensic Assessors:** Adjusters verifying that an extortion payment occurred and tracing where victim funds went.
* **Cybersecurity Students & Researchers:** Academic investigators learning blockchain analysis, digital evidence handling, and applied machine learning.

### 9. Complete End-to-End Workflow Diagram

```text
+-----------------------------------------------------------------------------------+
|                           RANSOMWARE EXTORTION INCIDENT                           |
|       (Victim server encrypted -> Ransom note demands BTC payment to Wallet X)     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                             RANSOM PAYMENT EXECUTED                               |
|        (Victim transfers Bitcoins from exchange/custody to extortion wallet)      |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        BITCOIN WALLET LOOKUP (RANSOMTRACE)                         |
|   (Investigator inputs Wallet Address into SOC Console -> Validates Base58/Bech32)|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           BLOCKCHAIN DATA INGESTION                               |
|   (Live Mempool API Query OR Local Synthetic Benchmark Demonstration Dataset)      |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         FORENSIC DATA NORMALIZATION                               |
|        (Satoshis to BTC, UTC timestamps, UTXO Input/Output flow direction)        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        TRANSACTION BEHAVIORAL ANALYTICS                           |
|  (10 Metrics: Volume, In/Out Counts, Mean Amount, Counterparties, Time Intervals) |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         FUND-FLOW TOPOLOGY GRAPH (DEPTH 1)                        |
|  (NetworkX DiGraph: Inflow Senders -> Target Wallet -> Outflow Recipients)        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                      AI ANOMALY DETECTION (ISOLATION FOREST)                      |
|      (7 Features extracted -> Tree Path Isolation Scoring -> Normal/Low/Med/High) |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                       INVESTIGATIVE RISK SCORING (0-100)                          |
|  (5 Observable Indicators: Freq [20] + Var [15] + CP [20] + Speed [20] + ML [25])  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        DIGITAL EVIDENCE PRESERVATION                              |
|     (Canonical RFC 8785 JSON Formatting -> Python hashlib SHA-256 Fingerprint)    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        APPEND-ONLY CHAIN OF CUSTODY                               |
|  (ISO/IEC 27037 Audit Trail: COLLECTED -> HASHED -> STORED -> VERIFIED -> Immutable)|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        FORENSIC REPORT GENERATION (PDF)                           |
| (ReportLab Platypus Engine -> 13 Sections -> Section 65B Indian IT Act Certificate)|
+-----------------------------------------------------------------------------------+
```

---

# PART 2 — PROJECT ARCHITECTURE

RansomTrace uses a modern, modular, decoupled architecture:
1. **Client Tier (Presentation):** Next.js 16 (React 19) Single-Page Application running on Node.js.
2. **API & Logic Tier (Backend):** FastAPI (Python 3.11+) asynchronous microservice running on Uvicorn.
3. **Data & Storage Tier:** Relational database managed via SQLAlchemy ORM (SQLite for zero-config local execution; PostgreSQL supported for production) and local filesystem evidence vault.
4. **External Integration:** Mempool API for live public Bitcoin blockchain queries, with built-in offline synthetic fallback.

### ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------------------------+
|                                      USER BROWSER / SOC ANALYST                                |
+-----------------------------------------------------------------------------------------------+
                                                │
                                    HTTP / JSON (Port 3000)
                                                ▼
+-----------------------------------------------------------------------------------------------+
|                                  NEXT.JS FRONTEND (App Router)                                |
|  • Layout: Header, Sidebar, SOC Shell, Command Center                                         |
|  • Pages: /cases, /ingestion, /analytics, /graph, /ml-risk, /evidence, /custody, /reports     |
|  • Visualizations: Recharts (Volume & Distributions), D3.js (Force-Directed Graph)            |
|  • Client Library: src/lib/api.ts (Fetch wrappers & TypeScript types)                         |
+-----------------------------------------------------------------------------------------------+
                                                │
                                  REST API / JSON (Port 8000)
                                                ▼
+-----------------------------------------------------------------------------------------------+
|                                     FASTAPI BACKEND GATEWAY                                   |
|  • Security Middlewares: RequestSizeLimit (10MB), RateLimiter, SecurityHeaders, CORS           |
|  • Global Exception Handlers: Sanitized errors, UUID error tracking, No stack traces leaked    |
|  • Routers: /wallets, /cases, /analytics, /graph, /ml, /risk, /evidence, /reports, /dashboard |
+-----------------------------------------------------------------------------------------------+
       │                   │                    │                   │                   │
       ▼                   ▼                    ▼                   ▼                   ▼
+-------------+     +-------------+      +-------------+     +-------------+     +-------------+
| BLOCKCHAIN  |     |  ANALYTICS  |      | GRAPH ENGINE|     |  ML ENGINE  |     | RISK ENGINE |
|   SERVICE   |     |   SERVICE   |      |   SERVICE   |     |   SERVICE   |     |   SERVICE   |
| (Mempool    |     | (10 Core    |      | (NetworkX   |     | (Isolation  |     | (5 Indicator|
|  Client &   |     |  Observable |      |  DiGraph    |     |  Forest     |     |  0-100 Score|
|  Validator) |     |  Metrics)   |      |  Depth 1)   |     |  7 Features)|     |  Assessment)|
+-------------+     +-------------+      +-------------+     +-------------+     +-------------+
       │                   │                    │                   │                   │
       └───────────────────┴────────────────────┼───────────────────┴───────────────────┘
                                                │
                                                ▼
+-----------------------------------------------------------------------------------------------+
|                                 FORENSIC INTEGRITY SUBSYSTEM                                  |
|  • Evidence Service: Canonical JSON serialization & Python hashlib SHA-256 hashing            |
|  • Chain of Custody: Append-only audit logging (Immutable; edits blocked with 403 Forbidden)  |
|  • Report Service: ReportLab PDF engine compiling 13-section dossier + Sec 65B Certificate    |
+-----------------------------------------------------------------------------------------------+
                                                │
                                                ▼
+-----------------------------------------------------------------------------------------------+
|                                      DATA PERSISTENCE TIER                                    |
|  • SQLAlchemy ORM Models: InvestigationCase, Wallet, Transaction, Evidence, Custody, ML/Risk  |
|  • Database Engine: SQLite (ransomtrace.db) / PostgreSQL via Docker                           |
|  • Evidence Vault: Local directory ./data/evidence_vault                                      |
+-----------------------------------------------------------------------------------------------+
```

### Detailed Breakdown of Every Component

#### 1. Security & Middleware Layer
* **What it is:** A stack of ASGI middleware classes executed on every incoming HTTP request before it reaches router logic.
* **Why we need it:** Prevents Denial-of-Service (DoS) attacks, stops automated scraping, protects against cross-site scripting (XSS) and clickjacking, and prevents leaking internal Python stack traces to clients.
* **File:** `backend/app/core/security.py` and `backend/app/main.py`
* **Classes/Functions:** `RequestSizeLimitMiddleware`, `RateLimiterMiddleware`, `SecurityHeadersMiddleware`, `sanitize_input_text()`, `validation_exception_handler()`.
* **Input / Output:** Takes raw Starlette `Request`; returns modified `Response` with security headers or aborts with HTTP 413, 429, or 422.

#### 2. Blockchain Client & Ingestion Service
* **What it is:** An asynchronous HTTP client communicating with public Bitcoin blockchain explorers, paired with a Base58/Bech32 address validator.
* **Why we need it:** Bitcoin ledgers are public, but raw blockchain RPC nodes require 600+ GB of storage. Mempool API provides fast, indexed REST queries.
* **Files:** `backend/app/services/mempool_client.py` and `backend/app/services/blockchain_service.py`
* **Classes/Functions:** `MempoolClient`, `validate_bitcoin_address()`, `BlockchainService.get_wallet_overview()`, `normalize_tx_data()`.
* **Input / Output:** Input: Bitcoin address string. Output: Normalized `WalletStatsResponse` and list of `TransactionResponse` objects with Satoshis, BTC, timestamps, and input/output addresses.

#### 3. Behavioral Analytics Engine
* **What it is:** A collection of 10 standalone, deterministic mathematical functions that calculate statistics on transaction histories.
* **Why we need it:** Forensic examiners need quick answers on total value moved, largest transactions, counterparty counts, and frequency without manual spreadsheet math.
* **File:** `backend/app/services/analytics_service.py`
* **Classes/Functions:** `AnalyticsService`, `calculate_total_transactions()`, `calculate_average_transaction_amount()`, `calculate_unique_counterparties()`, `calculate_average_time_between_tx_hours()`.
* **Input / Output:** Input: List of `TransactionResponse` objects. Output: `WalletAnalyticsResponse` containing the 10 metrics, daily volume timeline, amount distribution buckets, and bursts.

#### 4. Directed Fund-Flow Graph Engine
* **What it is:** A graph modeling service that translates Bitcoin transactions into nodes and directed edges using NetworkX.
* **Why we need it:** Enables visual tracking of fund dispersion from victim to extortionist to laundering hops.
* **File:** `backend/app/services/graph_service.py`
* **Classes/Functions:** `GraphService.build_fund_flow_graph()`, `make_short_label()`.
* **Input / Output:** Input: Target wallet address and transaction list. Output: `FundFlowGraphResponse` containing nodes, directed edges, and NetworkX topological metrics (density, degree).

#### 5. Machine Learning Anomaly Detection Service
* **What it is:** An unsupervised outlier detection engine using scikit-learn's Isolation Forest algorithm across 7 extracted features.
* **Why we need it:** High-throughput wallets with peeling behaviors exhibit statistical deviations from typical personal wallets. Unsupervised learning flags these outliers without requiring impossible "ransomware labels."
* **File:** `backend/app/services/ml_service.py`
* **Classes/Functions:** `MLAnomalyService`, `extract_features()`, `generate_simple_explanations()`.
* **Input / Output:** Input: Observed transactions for an address. Output: `MLAnalysisResponse` with raw score, 0–100 normalized score, classification tier (`NORMAL`, `LOW`, `MEDIUM`, `HIGH`), and human-readable feature deviations.

#### 6. Hybrid Risk Scoring Engine
* **What it is:** A transparent 0–100 scoring model that evaluates 5 observable behavioral indicators (frequency, variation, counterparties, fund velocity, and ML score).
* **Why we need it:** Investigators need prioritized triage. A composite score gives SOC analysts immediate insight into how unusual a wallet's activity is.
* **File:** `backend/app/services/risk_service.py`
* **Classes/Functions:** `RiskScoringService`, `calculate_simple_risk_score()`, `determine_risk_level()`.
* **Input / Output:** Input: Transaction list, address, and optional ML score. Output: `RiskAssessmentResponse` with 0–100 score, tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), factor breakdown, and mandatory disclaimer.

#### 7. Digital Evidence Locker & Chain of Custody
* **What it is:** An ISO/IEC 27037 compliant digital evidence repository that canonicalizes transaction findings, computes SHA-256 hashes, and records append-only custodial actions.
* **Why we need it:** In legal trials, digital evidence is thrown out if the defense can argue the investigator modified data after collection. Immutable hashes prove integrity.
* **File:** `backend/app/services/evidence_service.py`
* **Classes/Functions:** `EvidenceService`, `create_canonical_representation()`, `generate_evidence_hash()`, `verify_evidence_hash()`, `preserve_evidence_record()`.
* **Input / Output:** Input: Transaction details and case ID. Output: `SimpleEvidenceRecord` with SHA-256 fingerprint; verification returns `INTEGRITY VERIFIED` or `INTEGRITY CHECK FAILED`.

#### 8. PDF Forensic Report Generator
* **What it is:** A document compiler utilizing ReportLab's Platypus flowable framework to produce multi-page, formatted PDF investigation dossiers.
* **Why we need it:** Provides an executive and judicial document containing all findings, hashes, and an automated Section 65B Indian Evidence Act certificate for courtroom submission.
* **File:** `backend/app/services/report_service.py`
* **Classes/Functions:** `ForensicReportService.generate_pdf_report()`, `NumberedCanvas`.
* **Input / Output:** Input: Case ID and database session. Output: Raw PDF byte stream downloadable via browser.

#### 9. Relational Data Layer & Persistence
* **What it is:** SQLAlchemy ORM database models mapping investigation cases, wallets, transactions, evidence, custody entries, and risk assessments to SQLite or PostgreSQL.
* **Why we need it:** Allows investigators to save cases, resume investigations, look up past evidence, and maintain historical audit logs.
* **Files:** `backend/app/core/database.py`, `backend/app/models/`, `backend/app/services/data_layer.py`
* **Classes/Functions:** `BaseModel`, `InvestigationCase`, `Wallet`, `Transaction`, `Evidence`, `ChainOfCustodyEntry`, `RiskAssessment`, `MLAnalysis`, `init_database()`, `load_demo_data()`.
* **Input / Output:** Persists Python objects into relational tables and executes ACID queries.

---

# PART 3 — TECHNOLOGY STACK

This table lists **only** the technologies, libraries, and frameworks that exist and are actively used in the RansomTrace codebase.

| Technology | Purpose in Project | Where it is Used | Why it was Selected | What Students Need to Know |
| :--- | :--- | :--- | :--- | :--- |
| **Python (3.11+)** | Core backend language | Entire `backend/` directory | Dominant language for cybersecurity, forensics, and machine learning; clean syntax, robust standard library. | Python executes all backend services, algorithms, and data processing. |
| **FastAPI (0.110+)** | Asynchronous REST API framework | `backend/app/main.py`, `backend/app/api/v1/` | High performance, native async/await, automated OpenAPI (Swagger) documentation, and Pydantic validation. | Exposes endpoints like `/wallets/{address}` and `/cases`. Handles request routing and JSON serialization. |
| **Pydantic (v2) & Pydantic-Settings** | Data validation, type enforcement, settings | `backend/app/schemas/`, `backend/app/core/config.py` | Enforces strict schemas for incoming JSON, converts types, and reads `.env` variables cleanly. | Validates user input before processing. Returns clean validation errors if fields are missing or wrong type. |
| **SQLAlchemy (2.0+)** | Relational Object-Relational Mapper (ORM) | `backend/app/models/`, `backend/app/core/database.py` | Dialect-agnostic SQL abstraction; enables writing Python classes that map to SQLite or PostgreSQL. | Converts database rows into Python objects (e.g. `db.query(Wallet).filter(...)`). |
| **SQLite** | Zero-configuration local database | Root `ransomtrace.db` | Serverless, file-based SQL database built into Python. Zero setup required for student demos. | Default database engine storing cases, transactions, evidence, and custody logs. |
| **Alembic (1.13+)** | Database schema migration tool | `backend/alembic/` | Tracks database schema changes over time with versioned migration scripts. | Allows updating database tables (adding columns, constraints) without wiping existing data. |
| **HTTPX (0.27+)** | Asynchronous HTTP client | `backend/app/services/mempool_client.py` | Modern async HTTP client supporting timeouts, connection pooling, and non-blocking I/O. | Sends HTTP GET requests to the external Mempool blockchain API without blocking the FastAPI server. |
| **Scikit-learn (1.4+)** | Machine learning library | `backend/app/services/ml_service.py` | Gold standard open-source ML library in Python; provides efficient, clean implementation of Isolation Forest. | Used strictly for unsupervised anomaly detection (`IsolationForest`). Does not do classification or deep learning. |
| **NumPy (1.26+)** | Numerical computing | `backend/app/services/ml_service.py` | Fast array structures and mathematical operations needed to pass feature matrices into scikit-learn. | Shapes the 7 extracted behavioral features into 2D matrices (`np.array`) for the ML model. |
| **NetworkX (3.2+)** | Graph analysis and topology | `backend/app/services/graph_service.py` | Standard Python library for the creation, manipulation, and study of complex directed networks. | Constructs the directed graph (`DiGraph`), adds nodes (wallets) and edges (transactions), and calculates graph density and node degrees. |
| **ReportLab (4.1+)** | PDF generation engine | `backend/app/services/report_service.py` | Low-level and Platypus programmatic PDF publishing engine; draws precise tables, headers, footers, and text. | Generates the official court-admissible forensic PDF report dynamically in memory without external tools. |
| **hashlib** | Cryptographic hashing | `backend/app/services/evidence_service.py`, `mempool_client.py` | Built-in Python standard library implementing SHA-256 and other cryptographic digest algorithms in C. | Computes deterministic SHA-256 fingerprints of digital evidence artifacts and verifies their integrity. |
| **Uvicorn** | ASGI web server | `backend/app/main.py` entrypoint | Lightning-fast ASGI server for running asynchronous Python web frameworks. | Serves the FastAPI application on `http://localhost:8000`. |
| **Next.js (16 / App Router)** | Frontend React framework | Entire `frontend/` directory | Modern React framework with server-side rendering, file-based routing (`app/` directory), and optimized builds. | Hosts the Single-Page Application user interface and SOC command center on `http://localhost:3000`. |
| **TypeScript (v5)** | Strongly-typed frontend language | `frontend/src/**/*.ts`, `*.tsx` | Prevents runtime JavaScript errors by enforcing compile-time type safety across all frontend components. | Defines interfaces (`types.ts`) matching backend Pydantic schemas, ensuring data compatibility. |
| **Tailwind CSS (v4)** | Utility-first CSS styling | `frontend/src/app/globals.css` | Fast, modern CSS framework for building custom dark-mode Security Operations Center (SOC) aesthetics. | Provides styling classes (e.g., `bg-slate-900`, `border-cyan-500`) for the cyber-themed visual design. |
| **Recharts (3.10+)** | React charting library | `frontend/src/app/analytics/`, `page.tsx` | Composable, declarative React charting library built on SVG. | Renders interactive volume timelines, amount distribution histograms, and risk breakdowns in the browser. |
| **D3.js (v7)** | Data visualization library | `frontend/src/app/graph/page.tsx` | Industry standard JavaScript library for manipulating documents based on data; powerful force simulations. | Renders the interactive, animated directed fund-flow graph where users can drag nodes and inspect edges. |
| **Lucide React** | UI iconography | Throughout `frontend/src/components/` | Clean, modern SVG icon library matching modern cybersecurity dashboard standards. | Renders shield, alert, search, database, file, and network icons across the frontend interface. |
| **Mempool API** | Public blockchain data provider | Queried via `mempool_client.py` | Free, public, highly reliable Bitcoin block explorer REST API (`https://mempool.space/api`). | The external data source used to fetch real-world Bitcoin address balances, transaction history, and UTXO states. |

*(Note: Pandas and Plotly are not in requirements or package dependencies and are not used in this project.)*

---

# PART 4 — PROJECT FOLDER STRUCTURE

Here is the actual directory and file layout of RansomTrace:

```text
cybersecproj/
├── .env                              # Environment configuration (DB URL, CORS, API endpoints)
├── .env.example                      # Template for environment settings
├── README.md                         # Project documentation and quickstart instructions
├── docker-compose.yml                # Optional container setup for PostgreSQL database
├── ransomtrace.db                    # Active SQLite database file
├── data/
│   ├── evidence_vault/               # Directory for preserved JSON evidence artifacts
│   └── sample_cases/
│       └── wannacry_sample.json      # Pre-packaged WannaCry benchmark forensic case
├── backend/
│   ├── requirements.txt              # Python package dependencies
│   ├── alembic.ini                   # Alembic database migration configuration
│   ├── alembic/                      # Database migration versions and environments
│   ├── tests/                        # Comprehensive pytest test suite (14 test files)
│   └── app/
│       ├── main.py                   # FastAPI application initialization & middleware stack
│       ├── core/
│       │   ├── config.py             # Pydantic Settings class loading .env variables
│       │   ├── database.py           # SQLAlchemy database engine and session factory
│       │   └── security.py           # OWASP security middleware, rate limiter, regex validators
│       ├── models/                   # SQLAlchemy ORM database table definitions
│       │   ├── base.py               # Abstract BaseModel with UUID primary key & timestamps
│       │   ├── case.py               # InvestigationCase table model
│       │   ├── wallet.py             # Wallet and WalletRelation table models
│       │   ├── transaction.py        # Transaction table model
│       │   ├── evidence.py           # Evidence table model
│       │   ├── custody.py            # ChainOfCustodyEntry table model
│       │   └── analysis.py           # RiskAssessment and MLAnalysis table models
│       ├── schemas/                  # Pydantic request/response validation schemas
│       │   ├── health.py             # Health check schemas
│       │   ├── case.py               # Case creation & response schemas
│       │   ├── wallet.py             # Wallet statistics & transaction schemas
│       │   ├── analytics.py          # Behavioral metrics & distribution schemas
│       │   ├── graph.py              # Node, edge, and fund-flow graph response schemas
│       │   ├── ml.py                 # Isolation Forest feature breakdown & response schemas
│       │   ├── risk.py               # 5-Indicator risk scoring request & response schemas
│       │   ├── evidence.py           # Evidence preservation & verification schemas
│       │   ├── report.py             # Report preview schemas
│       │   └── dashboard.py          # Command center summary schemas
│       ├── services/                 # Pure Python business logic and algorithm engines
│       │   ├── mempool_client.py     # HTTP client for public Mempool API & Base58 validator
│       │   ├── blockchain_service.py # Ingestion service, normalization, demo mode routing
│       │   ├── analytics_service.py  # 10 core observable metric calculation functions
│       │   ├── graph_service.py      # NetworkX directed fund-flow graph builder (depth 1)
│       │   ├── ml_service.py         # Isolation Forest anomaly detection engine (7 features)
│       │   ├── risk_service.py       # Transparent 5-indicator risk scoring engine (0-100)
│       │   ├── evidence_service.py   # Canonical JSON serialization, SHA-256, & custody service
│       │   ├── report_service.py     # ReportLab Platypus PDF compilation service
│       │   ├── dashboard_service.py  # Aggregator for global SOC overview statistics
│       │   └── data_layer.py         # Direct CRUD helpers & synthetic demo dataset loader
│       └── api/
│           └── v1/                   # FastAPI route controllers
│               ├── router.py         # Master router aggregating all sub-routers
│               ├── health.py         # GET /health and GET /api/v1/health
│               ├── dashboard.py      # GET /dashboard/summary
│               ├── cases.py          # CRUD endpoints for investigation cases
│               ├── wallets.py        # GET /wallets/{addr} and /wallets/{addr}/transactions
│               ├── analytics.py      # GET /wallets/{addr}/analytics
│               ├── graph.py          # GET /wallets/{addr}/graph
│               ├── ml.py             # POST /ml/analyze and GET /ml/model-info
│               ├── risk.py           # POST /risk/assess and GET /risk/history
│               ├── evidence.py       # POST /evidence, POST /verify, POST /custody
│               └── reports.py        # GET /cases/{id}/report/pdf and /preview
└── frontend/
    ├── package.json                  # Next.js, React, Tailwind, D3, Recharts dependencies
    ├── tsconfig.json                 # TypeScript compiler configuration
    ├── next.config.ts                # Next.js configuration
    └── src/
        ├── lib/
        │   ├── types.ts              # TypeScript interface definitions matching backend schemas
        │   └── api.ts                # Client-side fetch wrapper functions
        ├── components/
        │   ├── layout/               # Header, Sidebar, and SOCShell wrappers
        │   └── dashboard/            # SystemMetrics, QuickActions, SyllabusRoadmap cards
        └── app/                      # Next.js App Router pages
            ├── page.tsx              # SOC Command Center dashboard
            ├── layout.tsx            # Global layout shell
            ├── globals.css           # Global Tailwind CSS definitions
            ├── ingestion/page.tsx    # Wallet Lookup & Blockchain Ingestion page
            ├── cases/page.tsx        # Investigation Cases Management page
            ├── analytics/page.tsx    # Behavioral Analytics & Distributions page
            ├── graph/page.tsx        # Interactive D3 Fund Flow Graph page
            ├── ml-risk/page.tsx      # Machine Learning Anomaly Detection page
            ├── risk/page.tsx         # Hybrid Risk Scoring & Indicators page
            ├── evidence/page.tsx     # Digital Evidence Locker & Tamper Verification page
            ├── custody/page.tsx      # Chronological Chain of Custody Timeline page
            ├── reports/page.tsx      # PDF Report Generator & Download page
            └── legal/page.tsx        # Legal & Ethical Boundaries reference page
```

---

# PART 5 — COMPLETE DATA FLOW

Here is the exact step-by-step lifecycle of an investigation query in RansomTrace, tracing a wallet address from the browser to the backend and down to the database and PDF report.

```text
[User inputs Address in UI]
           │
           ▼
1. Frontend Validation (Next.js)
           │
           ▼
2. HTTP POST/GET to Backend API (FastAPI)
           │
           ▼
3. Security Middleware Check (Rate Limiter, Size Limit, Security Headers)
           │
           ▼
4. Cryptographic Address Validation (Base58Check / Bech32 regex in Python)
           │
           ▼
5. Route Handler Execution (e.g. /wallets/{address})
           │
           ▼
6. Ingestion Branch: Demo Dataset OR Live Mempool API (blockchain_service.py)
           │
           ▼
7. Data Normalization (Satoshis -> BTC, Unix -> ISO UTC, Flow Direction)
           │
           ▼
8. Persistence & Cache Check (Save Wallet & Transactions in SQLite via SQLAlchemy)
           │
           ▼
9. Behavioral Analytics Calculation (10 metrics in analytics_service.py)
           │
           ▼
10. Fund-Flow Graph Construction (NetworkX DiGraph depth 1 in graph_service.py)
           │
           ▼
11. Feature Extraction (7 features in ml_service.py)
           │
           ▼
12. Isolation Forest Scoring (Anomaly path length & 0-100 calibration)
           │
           ▼
13. Risk Assessment (5 indicators evaluated: 0-100 score in risk_service.py)
           │
           ▼
14. Evidence Preservation (Canonical JSON formatting in evidence_service.py)
           │
           ▼
15. Cryptographic Fingerprinting (SHA-256 via Python hashlib)
           │
           ▼
16. Append-Only Chain of Custody Logging (ChainOfCustodyEntry in database)
           │
           ▼
17. PDF Forensic Report Compilation (ReportLab Platypus engine in report_service.py)
```

### File and Function Trace Table

| Step | Action | Responsible File | Responsible Function / Class |
| :---: | :--- | :--- | :--- |
| **1** | User enters wallet address in web form | `frontend/src/app/ingestion/page.tsx` | React form handler `handleSubmit()` |
| **2** | Input validation on client | `frontend/src/app/ingestion/page.tsx` | Regex string checks |
| **3** | HTTP Request dispatched to API | `frontend/src/lib/api.ts` | `getWalletOverview(address)` |
| **4** | Security middleware inspection | `backend/app/core/security.py` | `RateLimiterMiddleware`, `SecurityHeadersMiddleware` |
| **5** | Address cryptographic validation | `backend/app/services/mempool_client.py` | `validate_bitcoin_address()` |
| **6** | Ingestion & live API / demo routing | `backend/app/services/blockchain_service.py` | `BlockchainService.get_wallet_overview()` |
| **7** | External blockchain retrieval | `backend/app/services/mempool_client.py` | `MempoolClient.get_address_summary()` |
| **8** | Transaction forensic normalization | `backend/app/services/blockchain_service.py` | `normalize_tx_data()` |
| **9** | Relational storage & caching | `backend/app/models/wallet.py`, `transaction.py` | SQLAlchemy `db.add()`, `db.commit()` |
| **10** | 10 Observable analytics metrics | `backend/app/services/analytics_service.py` | `AnalyticsService.calculate_wallet_analytics()` |
| **11** | Directed fund-flow graph generation | `backend/app/services/graph_service.py` | `GraphService.build_fund_flow_graph()` |
| **12** | 7-Feature extraction for ML | `backend/app/services/ml_service.py` | `extract_features()` |
| **13** | Isolation Forest outlier scoring | `backend/app/services/ml_service.py` | `MLAnomalyService.score_wallet()` |
| **14** | 5-Indicator risk score evaluation | `backend/app/services/risk_service.py` | `calculate_simple_risk_score()` |
| **15** | Canonical JSON representation | `backend/app/services/evidence_service.py` | `create_canonical_representation()` |
| **16** | SHA-256 fingerprint generation | `backend/app/services/evidence_service.py` | `generate_evidence_hash()` using `hashlib.sha256()` |
| **17** | Append-only custody entry logged | `backend/app/models/custody.py` | `EvidenceService.create_evidence()` |
| **18** | Forensic PDF report compiled | `backend/app/services/report_service.py` | `ForensicReportService.generate_pdf_report()` |

---

# PART 6 — BITCOIN AND BLOCKCHAIN BASICS

To understand RansomTrace's code, students must understand the foundational blockchain concepts upon which the system is built.

### 1. What is cryptocurrency?
A **cryptocurrency** is a digital, decentralized medium of exchange that relies on cryptographic principles (public-key cryptography, hashing, and digital signatures) rather than a central bank or government to secure transactions, verify transfers, and prevent counterfeit creation.

### 2. What is Bitcoin?
**Bitcoin** is the first decentralized digital currency, introduced in 2008 by an anonymous programmer or group under the pseudonym Satoshi Nakamoto. It operates on a peer-to-peer network where transactions are validated by distributed consensus without intermediaries.

### 3. What is a blockchain?
A **blockchain** is an append-only, distributed ledger of records (blocks) that are cryptographically linked together. Once data is written to a confirmed block, it cannot be altered retroactively without recalculating all subsequent blocks and gaining control of the majority of the network's computing power (Proof-of-Work).

### 4. What is a block?
A **block** is a data container within the blockchain that holds a batch of verified transactions, a timestamp, a reference (hash) to the immediate previous block, and a cryptographic nonce satisfying the network's Proof-of-Work difficulty target.

### 5. What is a transaction?
A **transaction** is a signed cryptographic message broadcast to the network that transfers ownership of a specific quantity of Bitcoin from one or more senders to one or more receivers.

### 6. What is a transaction hash (TXID)?
A **transaction hash (TXID)** is an exact 64-character hexadecimal string generated by double-SHA-256 hashing the raw binary serialization of the transaction:
$$\text{TXID} = \text{SHA-256}(\text{SHA-256}(\text{RawTransactionBytes}))$$
The TXID serves as the unique, immutable global identifier for that transfer across the entire Bitcoin ledger.

### 7. What is a Bitcoin address?
A **Bitcoin address** is an alphanumeric string (typically 26 to 62 characters) derived from the public key of an asymmetric cryptographic key pair. It functions similarly to an account number or email address to which funds can be sent.
* **Legacy (P2PKH - Pay-to-PubKey-Hash):** Starts with `1` (e.g., `13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94`).
* **Script Hash (P2SH):** Starts with `3` (e.g., `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy`).
* **Native SegWit (Bech32):** Starts with `bc1q` (e.g., `bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq`).
* **Taproot (Bech32m):** Starts with `bc1p`.

### 8. What are inputs?
**Inputs (`vin`)** are references to funds previously received by the sender that are now being spent in the current transaction. Each input points to a previous transaction's specific output (TXID + index) and provides a cryptographic signature unlocking those coins.

### 9. What are outputs?
**Outputs (`vout`)** define where the Bitcoins are being sent. Each output specifies an amount in Satoshis and the recipient's locking script (address).

### 10. What is UTXO (Unspent Transaction Output)?
Bitcoin does **not** use an account-balance model (like an Ethereum account or a traditional bank account). Instead, Bitcoin uses the **UTXO (Unspent Transaction Output)** model:
* Think of UTXOs like physical currency bills or gold coins.
* If you have a $50 bill and want to buy a $20 item, you cannot "tear off" $20. You must hand over the entire $50 bill (input), the merchant takes $20 (output 1), and hands you a $30 bill as change (output 2).
* In Bitcoin, a wallet's "balance" is simply the mathematical sum of all unspent outputs currently controlled by its private keys.

### 11. What is a public blockchain?
A **public blockchain** is permissionless: anyone can download the client, join the peer-to-peer network, validate transactions, mine blocks, and query the complete transaction history without authorization or authentication.

### 12. What information is publicly visible?
On the Bitcoin public ledger, the following data is **100% visible to anyone**:
* Every transaction ID (TXID).
* The sender addresses (via unlocked previous outputs).
* The recipient addresses.
* The exact amount transferred in Satoshis / BTC.
* The mining fee paid.
* The exact block height and Unix timestamp when the block was confirmed.

### 13. What information is NOT publicly visible?
* ❌ Real names, passport numbers, or corporate registrations of wallet owners.
* ❌ Physical IP addresses or geographic locations of the sender or receiver.
* ❌ Private keys or passwords.
* ❌ The physical goods or services being paid for (e.g., ransom note details).

### 14. Can a Bitcoin address directly identify a person?
**No.** A Bitcoin address is **pseudonymous**, not anonymous. It is a cryptographic hash. Linking a Bitcoin address to a living person requires external intelligence, such as subpoenas to centralized KYC exchanges (Coinbase, Binance, Kraken) where the suspect converted crypto into fiat currency, or correlation with IP addresses captured during network transmission.

### 15. Why is blockchain useful for investigation?
Because the ledger is **immutable** and **globally transparent**:
* Suspects cannot delete, alter, or backdate old transactions.
* Once ransom funds leave the victim's wallet, investigators can follow every hop through the network in real-time.
* Historical transactions remain available forever, enabling retrospective analysis years after an attack.

### Concept vs. RansomTrace Implementation Table

| Blockchain Concept | Real-World Concept | How RansomTrace Uses It in Code |
| :--- | :--- | :--- |
| **Satoshi** | Smallest unit of Bitcoin ($1\text{ BTC} = 100,000,000\text{ Satoshis}$) | Defined as `SATS_PER_BTC = 100_000_000` in `blockchain_service.py`. All database math uses integer Satoshis to avoid floating-point rounding errors, then converts to BTC using `sats_to_btc()`. |
| **Address Validation** | Cryptographic Base58Check and Bech32 encoding | Validated in `backend/app/services/mempool_client.py` using `validate_bitcoin_address()` and regexes in `security.py`. |
| **UTXO Inputs/Outputs** | Transaction components (`vin` / `vout`) | Extracted in `normalize_tx_data()` into structured Pydantic `TxIO` objects. Evaluates whether target address was a sender or receiver. |
| **Flow Direction** | Direction of funds relative to wallet | Computed in `normalize_tx_data()`: `INCOMING` if target address is in outputs, `OUTGOING` if target address is in inputs, `INTERNAL` if both. |
| **Transaction Hash** | 64-character double-SHA-256 identifier | Stored as `Transaction.txid` in SQLite; validated using regex `RE_TX_HASH = r"^[0-9a-fA-F]{64}$"`. |
| **Block Time** | Unix epoch timestamp of block confirmation | Converted to human-readable ISO 8601 strings using `format_timestamp_iso()` (e.g. `2024-05-14 10:15:30 UTC`). |

---

# PART 7 — BLOCKCHAIN API INTEGRATION

RansomTrace integrates with the **Mempool API** (`https://mempool.space/api`) to query live Bitcoin blockchain ledger data.

### Why We Use the Mempool API
1. **Zero Infrastructure Overhead:** Running a full Bitcoin node requires ~600 GB of high-speed NVMe storage, significant RAM, and days of initial block download (IBD).
2. **Open and Unauthenticated:** Mempool.space provides public REST endpoints for educational and forensic queries without requiring paid subscriptions or hardcoded API keys.
3. **High Reliability:** It is widely recognized as one of the most stable, accurate public explorers in the Bitcoin ecosystem.

### Endpoints Used in Our Codebase

| Endpoint | HTTP Method | Implementation Function | Purpose |
| :--- | :---: | :--- | :--- |
| `/api/address/{address}` | `GET` | `MempoolClient.get_address_summary()` | Fetches total Satoshis received, spent, current balance, and transaction count. |
| `/api/address/{address}/txs` | `GET` | `MempoolClient.get_address_transactions()` | Fetches the most recent 25 to 50 confirmed transactions for the address. |
| `/api/tx/{txid}` | `GET` | `MempoolClient.get_transaction()` | Fetches raw input/output breakdown, fee, and block confirmation for a specific TXID. |

### Simplified Request & Response Examples

#### 1. Address Summary Query
**Request:**
```http
GET https://mempool.space/api/address/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94 HTTP/1.1
Accept: application/json
User-Agent: RansomTrace-Forensic-Client/1.0
```

**Response (Simplified JSON):**
```json
{
  "address": "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
  "chain_stats": {
    "funded_txo_count": 8,
    "funded_txo_sum": 5218765400,
    "spent_txo_count": 8,
    "spent_txo_sum": 5218765400,
    "tx_count": 8
  },
  "mempool_stats": {
    "funded_txo_count": 0,
    "funded_txo_sum": 0,
    "spent_txo_count": 0,
    "spent_txo_sum": 0,
    "tx_count": 0
  }
}
```

#### How Our Code Normalizes This Response
In `backend/app/services/blockchain_service.py` (`BlockchainService.get_wallet_overview`):
```python
total_received = chain_stats.get("funded_txo_sum", 0) + mempool_stats.get("funded_txo_sum", 0)
total_sent = chain_stats.get("spent_txo_sum", 0) + mempool_stats.get("spent_txo_sum", 0)
balance = max(0, total_received - total_sent)
tx_count = chain_stats.get("tx_count", 0) + mempool_stats.get("tx_count", 0)
```
* `funded_txo_sum`: All Satoshis ever transferred into this address.
* `spent_txo_sum`: All Satoshis ever transferred out of this address.
* `balance`: $\text{Total Received} - \text{Total Sent}$.

### Error Handling & API Rate Limits
1. **HTTP 404 (Not Found):** If an address has never appeared in any transaction on the blockchain, Mempool returns 404. Our client gracefully handles this by returning a clean zero-balance record rather than crashing:
   ```python
   if resp.status_code == 404:
       return {"address": address, "chain_stats": {"funded_txo_sum": 0, "tx_count": 0, ...}}
   ```
2. **HTTP 429 (Rate Limit Exceeded):** If a user spams queries, public nodes throttle requests. Our client catches `429` and raises an informative error:
   ```python
   raise RuntimeError("Upstream blockchain rate limit exceeded. Please retry shortly.")
   ```
3. **Network Timeouts & Downtime:** All HTTP queries enforce a strict timeout (`settings.HTTP_TIMEOUT_SECONDS = 15`). If the network times out or fails, the code catches the exception and falls back to cached SQLite records:
   ```python
   except Exception as e:
       if db_wallet and db_wallet.tx_count is not None:
           return WalletStatsResponse(...) # Return cached database copy
   ```

### Why Presentations Should NOT Rely Solely on Live APIs
In an academic viva or project demonstration, relying 100% on live external internet APIs is risky:
* Campus Wi-Fi may block outbound connections or throttle bandwidth.
* Public API rate limits may trigger unexpectedly if multiple students test simultaneously.
* Upstream API providers can experience temporary maintenance outages.

**RansomTrace's Solution:** Built-in **Demonstration Mode (`load_demo_data()`)**. If an investigator enters a synthetic address (like `1DemoRansomCollectionWallet002`) or the benchmark WannaCry case (`13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94`), the backend serves clean, deterministic local forensic records from SQLite with zero external API calls.

---

# PART 8 — TRANSACTION ANALYSIS

The behavioral analytics engine in `backend/app/services/analytics_service.py` calculates **10 core observable metrics** from the normalized transaction records.

### The 10 Core Metrics

#### 1. Total Transactions (`total_tx_count`)
* **Definition:** The total count of all transactions (both incoming deposits and outgoing transfers) observed for this wallet.
* **Why it matters:** Differentiates single-use burn addresses from high-throughput collection hubs.
* **Formula:** $N = \text{len}(\text{transactions})$
* **Example:** If a wallet has 4 deposits and 2 withdrawals, $\text{Total Transactions} = 6$.

#### 2. Incoming Transactions (`incoming_tx_count`)
* **Definition:** The count of transactions where funds entered the wallet from external senders.
* **Why it matters:** Indicates the number of discrete extortion payments or victim deposits.
* **Code Implementation:**
  ```python
  def calculate_incoming_transactions(txs: List[TransactionResponse]) -> int:
      return sum(1 for tx in txs if tx.flow_direction == "INCOMING")
  ```

#### 3. Outgoing Transactions (`outgoing_tx_count`)
* **Definition:** The count of transactions where funds left the wallet to external recipients.
* **Why it matters:** Reflects fund disbursement, peeling chain execution, or cash-out attempts.
* **Code Implementation:**
  ```python
  def calculate_outgoing_transactions(txs: List[TransactionResponse]) -> int:
      return sum(1 for tx in txs if tx.flow_direction == "OUTGOING")
  ```

#### 4. Total Received (`total_received_btc` & `total_received_sats`)
* **Definition:** Cumulative sum of all Satoshis/BTC transferred into the wallet across its active history.
* **Why it matters:** Quantifies total gross extortion revenue collected by the threat actor.
* **Formula:** $\sum |\text{net\_value\_sats}|$ for all transactions where $\text{direction} == \text{"INCOMING"}$.
* **Numerical Example:** If Victim A pays 1.5 BTC and Victim B pays 2.0 BTC:
  $$\text{Total Received} = 1.5 + 2.0 = 3.5\text{ BTC } (350,000,000\text{ Satoshis})$$

#### 5. Total Sent (`total_sent_btc` & `total_sent_sats`)
* **Definition:** Cumulative sum of all Satoshis/BTC moved out of the wallet to subsequent hops.
* **Why it matters:** Shows whether the extortionist has already liquidated or moved the extorted funds.
* **Formula:** $\sum |\text{net\_value\_sats}|$ for all transactions where $\text{direction} == \text{"OUTGOING"}$.

#### 6. Average Transaction Amount (`avg_tx_amount_btc`)
* **Definition:** The arithmetic mean value transferred per active transaction.
* **Why it matters:** Ransomware gangs frequently demand standardized payment amounts (e.g., exactly 0.5 BTC or 2.0 BTC per victim).
* **Formula:**
  $$\text{Mean Amount} = \frac{\sum_{i=1}^{k} |\text{net\_value\_sats}_i|}{k}$$
  where $k$ is the count of non-zero transactions.
* **Numerical Example:** If a wallet has 3 transactions of 0.2 BTC, 0.4 BTC, and 0.9 BTC:
  $$\text{Sum} = 0.2 + 0.4 + 0.9 = 1.5\text{ BTC}$$
  $$\text{Average} = \frac{1.5}{3} = 0.5\text{ BTC}$$

#### 7. Largest Transaction (`max_amount_btc`)
* **Definition:** The maximum single transaction magnitude observed for the wallet.
* **Why it matters:** Highlights major lump-sum cashouts or principal victim extortion payments.
* **Formula:** $\max(|\text{net\_value\_btc}_1|, |\text{net\_value\_btc}_2|, \dots)$

#### 8. Smallest Transaction (`min_amount_btc`)
* **Definition:** The minimum non-zero single transaction magnitude observed.
* **Why it matters:** Detects test deposits, micro-dusting attacks, or peel change outputs.
* **Formula:** $\min(|\text{net\_value\_btc}_1|, |\text{net\_value\_btc}_2|, \dots)$ where magnitude $> 0$.

#### 9. Number of Unique Counterparties (`unique_counterparties_count`)
* **Definition:** The total count of distinct external Bitcoin addresses that have directly sent funds to or received funds from the target wallet.
* **Why it matters:** High counterparty counts indicate a high-volume collection wallet or distribution mixer.
* **Code Implementation (`calculate_unique_counterparties`):**
  ```python
  counterparties = set()
  for tx in txs:
      for vin in tx.inputs:
          if vin.address and vin.address != clean_target:
              counterparties.add(vin.address)
      for vout in tx.outputs:
          if vout.address and vout.address != clean_target:
              counterparties.add(vout.address)
  return len(counterparties)
  ```
* **Numerical Example:** If Wallet A receives deposits from Wallets B and C, and later sends funds to Wallets D and C:
  The distinct set of counterparties is $\{B, C, D\}$, so $\text{Count} = 3$.

#### 10. Average Time Between Transactions in Hours (`avg_time_between_tx_hours`)
* **Definition:** The mean time delta between consecutive chronological transactions.
* **Why it matters:** Distinguishes human-operated personal wallets (days or weeks between transfers) from automated scripts that peel and disperse funds within minutes.
* **Formula:**
  $$\text{Avg Interval (Seconds)} = \frac{\sum_{i=1}^{m-1} (t_{i+1} - t_i)}{m - 1}$$
  $$\text{Avg Hours} = \frac{\text{Avg Interval (Seconds)}}{3600}$$
* **Numerical Example:**
  * Transaction 1: 10:00 AM (Timestamp: 0)
  * Transaction 2: 12:00 PM (Timestamp: +7,200s, interval = 2 hrs)
  * Transaction 3: 04:00 PM (Timestamp: +21,600s, interval = 4 hrs)
  $$\text{Mean Interval} = \frac{2 + 4}{2} = 3.0\text{ Hours}$$

---

# PART 9 — FUND FLOW GRAPH

Graph analysis is a foundational discipline in digital forensics and network science.

### 1. What is a graph?
A **graph** $G = (V, E)$ is a mathematical structure consisting of a set of vertices/nodes $V$ and a set of edges $E$ that connect pairs of nodes.

### 2. What is a node?
A **node (vertex)** represents an entity. In RansomTrace, every node represents a **Bitcoin Wallet Address**.

### 3. What is an edge?
An **edge (link)** represents a relationship between two nodes. In RansomTrace, every edge represents a **confirmed transaction** transferring Bitcoins between two addresses.

### 4. What is a directed graph?
A **directed graph (DiGraph)** is a graph where edges have a defined direction (an arrow pointing from source to destination). Because cryptocurrency moves unidirectionally from sender to receiver, fund flows must always be modeled as a directed graph.

### 5. Representing Bitcoin Transactions as Graphs
Consider a transaction where Address A sends 2.5 BTC to Address B:
* Node 1: Address A (Sender)
* Node 2: Address B (Receiver)
* Directed Edge: $A \xrightarrow{\text{TXID: 9f7b... / Amount: 2.5 BTC}} B$

### 6. What is NetworkX?
**NetworkX** is the standard Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks. RansomTrace uses `networkx.DiGraph()` to assemble and analyze the transaction topology.

### 7. How Our Project Creates the Graph
In `backend/app/services/graph_service.py`:
1. The target wallet address is initialized as the primary central node:
   ```python
   G = nx.DiGraph()
   G.add_node(clean_target, node_type="TARGET", is_target=True, depth=0)
   ```
2. For every incoming transaction (`flow_direction == "INCOMING"`):
   * Each input address is created as an `INFLOW_SENDER` node (depth 1).
   * A directed edge is created: $\text{Sender} \rightarrow \text{Target}$.
3. For every outgoing transaction (`flow_direction == "OUTGOING"`):
   * Each output address is created as an `OUTFLOW_RECEIVER` node (depth 1).
   * A directed edge is created: $\text{Target} \rightarrow \text{Receiver}$.

### 8. What Nodes and Edges are Created
Each `GraphNode` contains:
* `id`: Full Bitcoin address.
* `short_label`: Compact label for UI display (e.g., `1DemoR...et002`).
* `node_type`: `TARGET`, `INFLOW_SENDER`, or `OUTFLOW_RECEIVER`.
* `received_btc` / `sent_btc`: Volume associated with this node.
* `degree`: Total connections computed by NetworkX.

Each `GraphEdge` contains:
* `source`: Sending address.
* `target`: Receiving address.
* `txid`: 64-character transaction hash.
* `amount_btc`: Value transferred in BTC.
* `block_time_iso`: Formatted UTC confirmation timestamp.
* `confirmed`: Boolean confirmation status.

### 9. What Graph Depth Means and Why Depth is Strictly 1
* **Depth 1:** Analyzes direct counterparties (the target wallet, who paid it directly, and who it paid directly).
* **Depth 2:** Recursively queries transactions for all counterparties of counterparties.
* **Depth 3+:** Further recursive crawls.

**Architectural Decision in RansomTrace:** Graph traversal is strictly **Depth 1** (direct 1-hop neighborhood).
* **Why?** Recursive multi-hop crawling on public blockchains causes combinatorial graph explosion. A single wallet interacting with an exchange (which has 500,000 transactions) would cause hundreds of thousands of downstream API queries, instantly triggering rate limits, memory exhaustion, and multi-minute freezing. Depth 1 ensures instantaneous, deterministic, explainable results suitable for undergraduate defense.

### Small Topological Example

```text
[Victim Wallet A] ────────> (1.5 BTC) ────────┐
                                              │
[Victim Wallet B] ────────> (2.0 BTC) ───────>▼
                                    [Target Extortion Wallet]
                                              │
                                              ├───────> (3.4 BTC) ───────> [Laundering Peel Wallet C]
                                              │
                                              └───────> (0.09 BTC) ──────> [Miner Fee / Exchange D]
```
* **Nodes:** 5 total (`Victim A`, `Victim B`, `Target`, `Peel C`, `Exchange D`).
* **Edges:** 4 directed edges.
* **Topological Metrics:** NetworkX computes density:
  $$\text{Density} = \frac{|E|}{|V|(|V| - 1)}$$

---

# PART 10 — MACHINE LEARNING BASICS

To explain the AI component in RansomTrace during a viva exam, students must understand machine learning fundamentals from scratch.

### 1. What is Machine Learning?
**Machine Learning (ML)** is a subfield of artificial intelligence where computer algorithms learn mathematical patterns, relationships, and decision rules directly from data, rather than relying exclusively on hand-written static if-then rules.

### 2. Supervised Learning
In **supervised learning**, the algorithm is trained on a labeled dataset where each example has an input $X$ and a known ground-truth answer $y$.
* *Example:* 10,000 emails labeled as "Spam" ($y=1$) or "Not Spam" ($y=0$). The model learns to map text features to the spam label.

### 3. Unsupervised Learning
In **unsupervised learning**, the algorithm is provided only input data $X$ with **zero labels** ($y$ is unknown). The model must discover natural clusters, underlying distributions, or statistical anomalies on its own.
* *Example:* Identifying credit card transactions that deviate from normal spending patterns without having a historical list of every fraud type.

### 4. Classification vs. Regression
* **Classification:** Predicts a discrete category (e.g., Cat vs. Dog, Malware vs. Benign).
* **Regression:** Predicts a continuous numerical value (e.g., predicting the price of a house or temperature tomorrow).

### 5. Anomaly Detection (Outlier Detection)
**Anomaly detection** is an unsupervised learning technique designed to identify rare data points, events, or observations that deviate significantly from the baseline behavior of the majority of data.

### 6. Why RansomTrace Uses Anomaly Detection (NOT Supervised Classification)
A common trap question in project vivas is: *"Why didn't you train a classifier to predict whether a wallet is WannaCry or LockBit?"*
Students must answer with the following technical reality:
1. **Lack of Ground-Truth Labels:** In the real world, cryptocurrency extortionists do not register their wallets with a public database. Legitimate ground-truth labels for ransomware wallets are sparse, constantly outdated, and biased.
2. **Threat Evolution:** Attackers constantly change obfuscation methods, peeling ratios, and split sizes. A supervised model trained on 2017 WannaCry transactions will fail against 2026 ransomware campaigns.
3. **The Goal is Prioritization:** The objective is to identify **unusual transaction behavior** that warrants human investigator triage, not to output a false claim of criminal guilt.

### The 7 Engineered Features Used by Our Model

In `backend/app/services/ml_service.py` (`extract_features`):

| Feature Name | Meaning | Why it Matters | How it is Calculated | Example Value | Baseline Reference |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **`transaction_count`** | Total observed transactions | Identifies high-activity collection wallets vs. dormant wallets | `float(len(txs))` | `8.0` | `5.0` |
| **`average_transaction_amount`** | Mean transaction magnitude in BTC | Large average values suggest commercial extortion vs. micro-transactions | $\frac{\sum |\text{net\_btc}|}{N}$ | `0.652\text{ BTC}` | `0.05\text{ BTC}` |
| **`incoming_count`** | Total deposit transactions | Reflects multiple victim inflows into a collection address | Count where direction is `INCOMING` | `6.0` | `3.0` |
| **`outgoing_count`** | Total disbursement transactions | Detects pass-through and rapid liquidation behavior | Count where direction is `OUTGOING` | `2.0` | `2.0` |
| **`unique_counterparties`** | Distinct external addresses | High counterparty counts signify fan-in collection or fan-out mixing | Size of unique counterparty address set | `7.0` | `4.0` |
| **`transaction_frequency`** | Average transactions per active operational day | Automated laundering scripts exhibit rapid bursts of transactions per day | $\frac{\text{Total Tx}}{\max(1.0, \text{Active Days})}$ | `4.2\text{ tx/day}` | `0.5\text{ tx/day}` |
| **`amount_variance`** | Statistical dispersion of transfer magnitudes | High variance indicates irregular splits; low variance indicates uniform payments | $\frac{\sum (x_i - \mu)^2}{N}$ across non-zero amounts | `0.145\text{ BTC}^2` | `0.02\text{ BTC}^2` |

---

# PART 11 — ISOLATION FOREST

This section explains the core machine learning algorithm implemented in RansomTrace.

### 1. What is Isolation Forest?
**Isolation Forest** is an unsupervised ensemble anomaly detection algorithm developed by Fei Tony Liu, Kai Ming Ting, and Zhi-Hua Zhou in 2008. Unlike other anomaly detection algorithms that construct profiles of normal points (like distance-based k-Means or density-based LOF), Isolation Forest **explicitly isolates anomalies**.

### 2. Why We Selected Isolation Forest
* **Efficiency:** It has linear time complexity $O(n \log n)$ and minimal memory consumption.
* **Handles Multi-Dimensional Data:** Performs effectively across multiple continuous features without requiring complex distance-metric scaling.
* **No Assumption of Normal Distribution:** Does not assume the blockchain features follow a Gaussian bell curve.

### 3. How It Works Conceptually
The algorithm is based on two simple, universal characteristics of anomalies:
1. They are the **minority** (few in number).
2. They have attribute values that are **statistically distinct** from normal instances.

Because of these two properties, **anomalies are much easier to isolate** from the rest of the dataset than normal points.

### 4. Decision Trees in Isolation Forest (iTrees)
Isolation Forest builds an ensemble of randomized decision trees called **Isolation Trees (iTrees)**:
1. A random feature is chosen from the feature set.
2. A random split value is chosen between the minimum and maximum values of that feature.
3. The dataset is split into two child nodes based on whether data points are less than or greater than this split value.
4. This recursive partitioning continues until every data point is isolated in its own leaf node, or the tree reaches a maximum height limit.

### 5. Why Anomalies Become Isolated Faster
Imagine a classroom of 50 students where 49 students are between 5 feet and 6 feet tall, but one student is 8 feet tall:
* If you make random horizontal cuts between 0 and 10 feet, a single random cut at 7 feet immediately isolates the 8-foot student all by themselves!
* To isolate any individual 5-foot-6 student among 49 peers, you will need many repeated cuts dividing the cluster over and over.

**Conclusion:**
* **Anomalies** have **short path lengths** from the root to the leaf (isolated in very few splits).
* **Normal points** have **deep path lengths** (buried deep inside dense clusters).

```text
NORMAL CLUSTER DATA POINT (Deep Path Length)       ANOMALOUS OUTLIER (Short Path Length)
                Root                                               Root
               /    \                                             /    \
             [Cut]  ...                                      [Cut 1]  ...
            /     \                                            /
         [Cut]    ...                                     [ANOMALY ISOLATED!]
        /     \                                           (Path Length = 1 split)
      [Cut]   ...
     /     \
 [NORMAL ISOLATED]
 (Path Length = 6 splits)
```

### 6. Anomaly Score Calculation
The anomaly score $s$ for an instance $x$ across an ensemble of $n$ trees is formulated as:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
* $h(x)$ is the path length (number of edges $x$ traverses from the root to the leaf).
* $E(h(x))$ is the expected (average) path length of $x$ across all trees in the forest.
* $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree (BST) for $n$ data points, serving as the normalization constant:
  $$c(n) = 2\left(\ln(n - 1) + 0.5772156649\right) - \frac{2(n - 1)}{n}$$
  *(where $0.5772156649$ is Euler's constant).*

**Score Interpretation:**
* If $E(h(x)) \to 0$, $s \to 2^0 = 1$ $\rightarrow$ **Definite Anomaly** (isolated almost immediately).
* If $E(h(x)) \to n - 1$, $s \to 0$ $\rightarrow$ **Highly Central / Normal Point**.
* If $E(h(x)) \to c(n)$, $s \to 0.5$ $\rightarrow$ Instance does not exhibit distinct anomalies.

### 7. How Our Code Converts the Model Output
In scikit-learn, `IsolationForest.decision_function(X)` returns an offset score:
* Large positive values (e.g. $+0.15$ to $+0.25$) indicate **normal, central points**.
* Negative values (e.g. $-0.10$ to $-0.25$) indicate **outliers / anomalies**.

In `backend/app/services/ml_service.py`, our code converts this raw output into a calibrated **0.0 to 100.0 Normalized Anomaly Score**:
```python
raw_score = float(clf.decision_function(feature_vector)[0])
normalized_score = round(float(np.clip(50.0 - (raw_score * 125.0), 5.0, 95.0)), 1)
```

#### Mapping to Anomaly Tiers:
* **`NORMAL`:** Normalized score $< 35.0$
* **`LOW ANOMALY`:** Normalized score $35.0$ to $54.9$
* **`MEDIUM ANOMALY`:** Normalized score $55.0$ to $74.9$
* **`HIGH ANOMALY`:** Normalized score $\ge 75.0$

### 8. Crucial Ethical & Academic Distinction
During a viva, **never say:**
> *"Isolation Forest proved this wallet belongs to a ransomware attacker."*

**Always say:**
> *"Isolation Forest detected that this wallet's transaction volume, velocity, and counterparty patterns represent a statistical outlier compared to baseline transaction profiles."*

---

# PART 12 — MACHINE LEARNING CODE EXPLANATION

Here is an annotated breakdown of the actual machine learning service in `backend/app/services/ml_service.py`.

### Block 1: Model Initialization and Hyperparameters
```python
class MLAnomalyService:
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.model_info = ModelInfo(
            model_name="IsolationForest",
            model_version="1.0.0",
            algorithm_type="Unsupervised Anomaly Detection",
            n_estimators=100,
            contamination=0.15,
            random_state=self.random_seed,
            framework="scikit-learn"
        )
```
* `n_estimators=100`: Builds an ensemble of 100 randomized decision trees. 100 trees provide an optimal balance between ensemble variance reduction and fast execution.
* `contamination=0.15`: Informs the algorithm that approximately 15% of the overall feature space is expected to contain anomalous behaviors.
* `random_state=42`: Seeds the pseudo-random number generator so tree splits are 100% deterministic and reproducible during grading.

### Block 2: Feature Matrix Assembly & Model Fitting
```python
feats = extract_features(txs, clean_addr)
feature_vector = np.array([[
    feats["transaction_count"],
    feats["average_transaction_amount"],
    feats["incoming_count"],
    feats["outgoing_count"],
    feats["unique_counterparties"],
    feats["transaction_frequency"],
    feats["amount_variance"],
]])

# Train IsolationForest on baseline corpus combined with observed sample
training_data = np.vstack([BASELINE_CORPUS, feature_vector])
clf = IsolationForest(
    n_estimators=self.model_info.n_estimators,
    contamination=self.model_info.contamination,
    random_state=self.random_seed
)
clf.fit(training_data)
```
* `extract_features()` extracts the 7 continuous numerical features.
* `BASELINE_CORPUS` is a 10-row reference array representing standard personal wallet profiles.
* `np.vstack([BASELINE_CORPUS, feature_vector])` stacks the observed wallet against the baseline reference corpus.
* `clf.fit(training_data)` constructs the 100 isolation trees over this combined space.

### Block 3: Scoring & Normalization
```python
raw_score = float(clf.decision_function(feature_vector)[0])
normalized_score = round(float(np.clip(50.0 - (raw_score * 125.0), 5.0, 95.0)), 1)
```
* `decision_function(feature_vector)[0]` calculates the average path length across all 100 trees.
* `raw_score * 125.0`: Inverts and scales the raw score so that negative outliers translate into higher risk numbers.
* `np.clip(..., 5.0, 95.0)`: Clamps extreme boundary spikes between 5.0 and 95.0 to avoid misleading 0% or 100% absolutes.

### Block 4: Explainable AI Attribution
```python
def generate_simple_explanations(features: Dict[str, float]) -> str:
    reasons: List[str] = []
    if features["transaction_frequency"] > 1.0:
        reasons.append("Unusually high transaction frequency was observed.")
    if features["amount_variance"] > 0.1:
        reasons.append("Transaction amounts show higher-than-normal variation.")
    if features["unique_counterparties"] >= 4:
        reasons.append("Multiple distinct counterparties were observed.")
    if features["average_transaction_amount"] > 1.0:
        reasons.append("High average transaction amounts detected compared to baseline transfers.")
    ...
```
* Generates clear natural-language explanations explaining *why* the wallet scored high, replacing opaque black-box AI with transparent indicators.

---

# PART 13 — RISK SCORING

RansomTrace implements a transparent **0 to 100 Investigative Risk Scoring System** in `backend/app/services/risk_service.py`.

### Why We Need Risk Scoring
In active Security Operations Centers (SOCs), incident responders receive dozens of suspicious wallet alerts daily. The risk score allows investigators to prioritize their triage queue immediately.

### The 5 Observable Indicators (Total = 100 Points)

| Indicator | Metric Evaluated | Max Points | Trigger Condition in Code |
| :--- | :--- | :---: | :--- |
| **1. Transaction Frequency** | Total observed transaction volume | **20 pts** | $\ge 15\text{ tx} \rightarrow 20\text{ pts}$<br>$\ge 8\text{ tx} \rightarrow 12\text{ pts}$<br>$\ge 3\text{ tx} \rightarrow 6\text{ pts}$ |
| **2. Amount Variation** | Statistical variance of transaction amounts | **15 pts** | $\text{Variance} \ge 1.0\text{ BTC}^2 \rightarrow 15\text{ pts}$<br>$\text{Variance} \ge 0.1\text{ BTC}^2 \rightarrow 8\text{ pts}$ |
| **3. Number of Counterparties** | Count of distinct senders & receivers | **20 pts** | $\ge 10\text{ counterparties} \rightarrow 20\text{ pts}$<br>$\ge 5\text{ counterparties} \rightarrow 12\text{ pts}$<br>$\ge 2\text{ counterparties} \rightarrow 6\text{ pts}$ |
| **4. Rapid Movement of Funds** | Average hours between consecutive transactions | **20 pts** | $\le 1.0\text{ hr} \rightarrow 20\text{ pts}$<br>$\le 6.0\text{ hrs} \rightarrow 12\text{ pts}$<br>$\le 24.0\text{ hrs} \rightarrow 6\text{ pts}$ |
| **5. ML Anomaly Result** | Isolation Forest normalized score | **25 pts** | $\frac{\text{Normalized ML Score}}{100.0} \times 25.0\text{ pts}$ |
| **TOTAL POSSIBLE SCORE** | Sum of all 5 indicators | **100 pts** | Sum of 1 through 5 |

### Operational Risk Tiers

$$\text{Final Score} = \text{Indicator}_1 + \text{Indicator}_2 + \text{Indicator}_3 + \text{Indicator}_4 + \text{Indicator}_5$$

* **`LOW` (0.0 – 29.9):** Standard dormant or low-activity personal wallet. Low investigation priority.
* **`MEDIUM` (30.0 – 59.9):** Moderate transaction activity with occasional counterparties. Routine monitoring.
* **`HIGH` (60.0 – 79.9):** Notable behavioral anomalies (rapid fund velocity, elevated variance, multiple counterparties). Priority investigation recommended.
* **`CRITICAL` (80.0 – 100.0):** Severe behavioral anomalies (rapid automated fund peeling, high transaction bursts, strong ML anomaly score). Immediate forensic containment recommended.

### Step-by-Step Numerical Example

Suppose an investigator analyzes an extortion wallet with the following metrics:
1. **Transaction Count:** 16 transactions $\rightarrow$ Triggers $\ge 15$ threshold $\rightarrow$ **+20.0 pts**
2. **Amount Variance:** $0.45\text{ BTC}^2$ $\rightarrow$ Triggers $\ge 0.1$ threshold $\rightarrow$ **+8.0 pts**
3. **Unique Counterparties:** 6 distinct addresses $\rightarrow$ Triggers $\ge 5$ threshold $\rightarrow$ **+12.0 pts**
4. **Fund Velocity:** Transactions occurred an average of 45 minutes (0.75 hrs) apart $\rightarrow$ Triggers $\le 1.0\text{ hr}$ threshold $\rightarrow$ **+20.0 pts**
5. **Isolation Forest Output:** Normalized ML score is $72.0$ $\rightarrow \frac{72.0}{100.0} \times 25.0 = \mathbf{+18.0\text{ pts}}$

**Total Risk Score Calculation:**
$$\text{Risk Score} = 20.0 + 8.0 + 12.0 + 20.0 + 18.0 = \mathbf{78.0}$$
* **Tier:** **`HIGH`** (since $60.0 \le 78.0 \le 79.9$).
* **Factors Generated:**
  * "High transaction frequency"
  * "High transaction amount variation"
  * "Large number of counterparties"
  * "Rapid movement of funds"
  * "High anomaly score"

---

# PART 14 — DIGITAL FORENSICS

### 1. What is Digital Forensics?
**Digital Forensics** is the branch of forensic science encompassing the identification, acquisition, preservation, analysis, and court-admissible presentation of digital evidence stored on or transmitted by electronic devices and computer networks.

### 2. What is Digital Evidence?
**Digital Evidence** is any probative information stored or transmitted in digital format that may be relied upon in a court of law. It is inherently fragile, volatile, and easily modified if not handled properly.

### 3. Relevance of Blockchain Data to Forensic Investigations
Because public blockchain records are immutable and cryptographically secured, they represent high-fidelity digital evidence. However, raw JSON files downloaded from the internet do not become admissible evidence automatically; they must be formally acquired, hashed, and tracked under established standards (ISO/IEC 27037).

### 4. The 5 Stages of the Digital Evidence Lifecycle

```text
1. IDENTIFICATION
   (Locating the extortion wallet address from ransom notes or malware configuration)
          │
          ▼
2. COLLECTION / ACQUISITION
   (Extracting raw transaction JSON payloads from the public blockchain ledger)
          │
          ▼
3. PRESERVATION
   (Computing SHA-256 hashes & storing in tamper-evident repository)
          │
          ▼
4. ANALYSIS
   (Examining counterparties, velocity, Isolation Forest anomalies, & risk scores)
          │
          ▼
5. REPORTING & PRESENTATION
   (Compiling PDF dossier with Section 65B Indian IT Act certificate for court)
```

### 5. How RansomTrace Maps to These Forensic Stages
* **Identification:** User creates an `InvestigationCase` and enters the target Bitcoin address.
* **Collection:** `MempoolClient` pulls transaction structures into structured `Transaction` models.
* **Preservation:** `EvidenceService.preserve_transaction()` canonicalizes the data and generates an immutable SHA-256 hash.
* **Analysis:** `AnalyticsService`, `GraphService`, `MLAnomalyService`, and `RiskScoringService` compute metrics.
* **Reporting:** `ForensicReportService` renders the PDF dossier with complete hash audit tables.

---

# PART 15 — SHA-256 IMPLEMENTATION

### 1. What is Hashing?
A **cryptographic hash function** is a mathematical algorithm that maps an arbitrary-sized block of input data to a fixed-size string of bytes (digest).
* **One-Way Function:** It is computationally infeasible to invert (you cannot deduce the input data from the hash).
* **Deterministic:** The exact same input will always produce the exact same hash.
* **Avalanche Effect:** Changing a single bit in the input completely alters the resulting hash.

### 2. Hashing vs. Encryption
Students frequently confuse these two concepts during vivas:

| Property | Hashing | Encryption |
| :--- | :--- | :--- |
| **Directionality** | **One-way** (cannot be reversed or decrypted) | **Two-way** (can be decrypted using the corresponding key) |
| **Key Required?** | No key required (pure mathematical digest) | Requires cryptographic key (symmetric or asymmetric) |
| **Output Length** | Fixed length (e.g. SHA-256 is always 256 bits / 64 hex characters) | Variable length (proportional to plaintext length) |
| **Primary Purpose** | **Integrity verification** (tamper detection) | **Confidentiality** (hiding plaintext from eavesdroppers) |

### 3. What is SHA-256?
**SHA-256 (Secure Hash Algorithm 256-bit)** is a cryptographic hash algorithm designed by the United States National Security Agency (NSA) and published by NIST in 2001 under FIPS PUB 180-4. It produces a 256-bit (32-byte) digest, rendered as a 64-character hexadecimal string.

### 4. Deterministic Canonical Serialization (RFC 8785 Principle)
A critical pitfall in digital evidence hashing is that standard JSON serialization is non-deterministic:
* `{"a": 1, "b": 2}` and `{"b": 2, "a": 1}` have the exact same data, but produce completely different SHA-256 hashes because the key order is different!
* Adding a single space (`{"a": 1}`) vs (`{"a":1}`) also changes the hash!

In `backend/app/services/evidence_service.py`, RansomTrace enforces **canonical serialization**:
```python
def create_canonical_representation(case_id, transaction_id, wallet_address, amount, timestamp, source):
    canonical_dict = {
        "amount": round(float(amount), 8) if amount is not None else 0.0,
        "case_id": str(case_id or "").strip(),
        "source": str(source or "").strip(),
        "timestamp": str(timestamp or "").strip(),
        "transaction_id": str(transaction_id or "").strip().lower(),
        "wallet_address": str(wallet_address or "").strip(),
    }
    return json.dumps(
        canonical_dict,
        sort_keys=True,               # Keys are strictly sorted alphabetically
        separators=(",", ":"),        # All whitespace eliminated
        ensure_ascii=True,
        default=str
    ).encode("utf-8")
```

### 5. Generating the Hash with Python `hashlib`
```python
def generate_evidence_hash(case_id, transaction_id, wallet_address, amount, timestamp, source):
    canonical_bytes = create_canonical_representation(...)
    return hashlib.sha256(canonical_bytes).hexdigest()
```

### 6. Integrity Verification Workflow
```text
Original Evidence Stored              Forensic Verification Request
           │                                        │
           ▼                                        ▼
Canonical Byte Serialization              Current Data Re-Serialized
           │                                        │
           ▼                                        ▼
hashlib.sha256()                          hashlib.sha256()
           │                                        │
           ▼                                        ▼
[Stored Hash: e3b0c442...]               [Computed Hash: e3b0c442...]
           │                                        │
           └──────────────────┬─────────────────────┘
                              ▼
                   Do both hashes match?
                     /              \
                   YES              NO
                   /                  \
        "INTEGRITY VERIFIED"   "INTEGRITY CHECK FAILED"
        (Evidence unchanged)    (Evidence was tampered with!)
```

---

# PART 16 — CHAIN OF CUSTODY

### 1. What Chain of Custody (CoC) Means
The **Chain of Custody** is a chronological, tamper-evident paper or digital trail documenting the acquisition, control, transfer, analysis, and disposition of physical or electronic evidence.

### 2. Why Chain of Custody Matters
In court, if an investigator presents a transaction report showing a ransom payment, the defense attorney will ask:
* *"Who collected this data?"*
* *"When was it captured?"*
* *"Where was it stored?"*
* *"How can you prove no one altered the numbers between seizure and today?"*

Without a continuous, verified Chain of Custody, digital evidence is deemed untrustworthy and ruled **inadmissible** in judicial proceedings.

### 3. What Information is Recorded
In `backend/app/models/custody.py` (`ChainOfCustodyEntry`):
* `id`: Unique UUID identifier for the custody event.
* `case_id`: Linked investigation case dossier.
* `evidence_id`: Specific evidence artifact identifier.
* `action_performed`: The specific custodial operation performed.
* `actor_name`: Name or badge number of the investigator / system process.
* `notes`: Contextual remarks describing the action.
* `previous_hash`: The SHA-256 fingerprint from the preceding custody record.
* `current_hash`: The current cryptographic fingerprint.
* `timestamp`: UTC datetime stamp recorded automatically at execution.

### 4. Valid Custodial Actions in Our Codebase
* `COLLECTED`: Raw transaction captured from the blockchain.
* `HASHED`: SHA-256 fingerprint generated.
* `STORED`: Persisted into the evidence vault.
* `VERIFIED`: Integrity check executed against stored hash.
* `ACCESSED`: Record opened for inspection.
* `REVIEWED`: Examined by lead forensic investigator.
* `TRANSFERRED`: Transferred to another analyst or legal counsel.
* `EXPORTED`: Exported into an external court report or archive.

### 5. Immutability Enforcement (Blocking Modifications)
In `backend/app/api/v1/evidence.py`, attempting to edit or delete a previously logged custody entry is explicitly forbidden:
```python
@router.put("/evidence/{evidence_id}/custody/{entry_id}")
@router.patch("/evidence/{evidence_id}/custody/{entry_id}")
def disallow_editing_custody_entry(evidence_id: str, entry_id: str):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Chain of custody entries are strictly immutable and cannot be edited. New actions must be appended."
    )
```
If an investigator makes an error or conducts a re-examination, they cannot change past records; they must append a new action.

---

# PART 17 — FORENSIC REPORT GENERATION

The PDF reporting subsystem is implemented in `backend/app/services/report_service.py` using **ReportLab Platypus**.

### The 13 Required Forensic Sections

| Section # | Title | Content Rendered in PDF |
| :---: | :--- | :--- |
| **1** | Title & Header Banner | Formal report title, security classification, unique report UUID, timestamp. |
| **2** | Case Information | Case ID, incident type, title, description, investigator name, date opened. |
| **3** | Wallet Information | Investigated Bitcoin address, address type (P2PKH/SegWit), balance, total received, total sent. |
| **4** | Transaction Summary Table | Breakdown of observed transactions (TXIDs, amounts in BTC, timestamps, directions). |
| **5** | Transaction Analytics | 10 metrics: In/Out counts, average amount, largest amount, velocity, counterparties. |
| **6** | Fund-Flow Graph Summary | Description of directed topological nodes (senders and receivers) at depth 1. |
| **7** | AI Anomaly Detection Result | Isolation Forest model parameters, raw path length score, normalized 0–100 score, tier. |
| **8** | Risk Assessment & Factors | Final 0–100 risk score, operational tier, and bulleted risk factors. |
| **9** | Evidence Inventory | Table listing all seized evidence artifacts with descriptions and collectors. |
| **10** | SHA-256 Cryptographic Hashes | Complete 64-character SHA-256 hash manifest for all preserved artifacts. |
| **11** | Chain of Custody History | Chronological log showing actions (`COLLECTED`, `HASHED`, `STORED`, `VERIFIED`). |
| **12** | Technical & Forensic Boundaries | Clear explanation of system limitations (no de-anonymization, no fund seizing). |
| **13** | Section 65B Indian IT Act Certificate | Mandatory statutory certificate declaring computerized record integrity. |

### The Two-Pass `NumberedCanvas`
A standard limitation of basic PDF generation is that the software does not know the total number of pages until the entire document has finished rendering.
In `report_service.py`, RansomTrace implements a custom `NumberedCanvas` class:
* Pass 1: Records all page layouts and contents in memory.
* Pass 2: Iterates through the saved pages and draws running headers and dynamic footers: `"Page X of Y"`.

### Report Compilation Process
```text
Investigator clicks "Generate PDF Report"
                   │
                   ▼
FastAPI calls forensic_report_service.generate_pdf_report(case_id, db)
                   │
                   ▼
Queries database for Case, Wallets, Transactions, Evidence, Custody, ML, & Risk records
                   │
                   ▼
Initializes io.BytesIO() buffer and ReportLab SimpleDocTemplate
                   │
                   ▼
Builds Platypus Flowables list (Paragraphs, Tables, Spacers, HRFlowables)
                   │
                   ▼
DocTemplate.build(story, canvasmaker=NumberedCanvas)
                   │
                   ▼
Returns raw PDF byte stream with HTTP header:
Content-Disposition: attachment; filename="RansomTrace_Forensic_Report_CASE-001.pdf"
```

---

# PART 18 — CYBERCRIME LIFECYCLE

Students should understand how RansomTrace fits into the broader timeline of a ransomware attack.

```text
1. RECONNAISSANCE ────────> Threat actors scan victim networks for exposed RDP ports, phishing targets.
        │
2. INITIAL ACCESS ────────> Phishing email opened, credential stuffing, or exploit kit executed.
        │
3. EXECUTION & LATERAL ───> Cobalt Strike / Mimikatz used to move across domain controllers.
        │
4. DATA EXFILTRATION ─────> Sensitive corporate data stolen (double-extortion tactic).
        │
5. ENCRYPTION ────────────> Ransomware binary executes, encrypting user and system files.
        │
6. RANSOM DEMAND ─────────> Ransom note dropped on desktop specifying BTC payment address.
        │
        ▼
========================================================================================
     RANSOMTRACE OPERATIONAL SCOPE (POST-INCIDENT FORENSICS & FINANCIAL TRACING)
========================================================================================
        │
7. PAYMENT EXECUTION ─────> Victim company pays ransom to obtain decryptor key.
        │
8. FUND MOVEMENT ─────────> Extortionists move Bitcoins through peeling chains & mixers.
        │
9. RANSOMTRACE FORENSICS ─> • Address lookup & transaction normalization
                            • Fund-flow graph reconstruction
                            • Machine learning anomaly detection
                            • 0–100 Risk prioritization
                            • SHA-256 evidence preservation & Chain of Custody
                            • Section 65B court-admissible PDF reporting
```

---

# PART 19 — LEGAL AND ETHICAL CONSIDERATIONS

### 1. Public Blockchain Data vs. Private Communications
* Transactions on the Bitcoin blockchain are broadcast publicly to thousands of global nodes and written to an open ledger.
* Accessing public ledger data does **not** constitute unauthorized interception of private communications or hacking under cyber laws.

### 2. Address Pseudonymity vs. Real-World Identity
* RansomTrace works exclusively with pseudonymous wallet addresses.
* It does not harbor or scrape personally identifiable information (PII).
* The application never asserts that a wallet belongs to a specific named human being.

### 3. Indian Information Technology (IT) Act, 2000 & Section 65B Compliance
Under Indian law, electronic records are admissible as evidence in court under **Section 65B of the Indian Evidence Act, 1872** (and corresponding provisions in the Bharatiya Sakshya Adhiniyam, 2023 / IT Act 2000).
* **Section 65B Certificate Requirements:** A certificate must accompany the electronic record stating:
  1. The electronic record was produced by a computer during its regular lawful use.
  2. The computer was operating properly throughout the period.
  3. The information reproduces data stored or processed by the system without unauthorized tampering.
* RansomTrace automatically appends this complete certificate to every generated PDF report.

### 4. Digital Personal Data Protection (DPDP) Act, 2023
* RansomTrace stores only publicly observable ledger hashes, timestamps, and amounts.
* It stores zero names, personal phone numbers, Aadhaar numbers, or biometric records, adhering to privacy-by-design standards.

### 5. Responsible Investigation & Ethical Boundaries
* All anomaly classifications and risk scores are probabilistic investigative indicators.
* They serve to guide law enforcement attention, never to establish definitive criminal liability or bypass due process.

---

# PART 20 — APPLICATION SECURITY

RansomTrace implements defense-in-depth protections across the backend. Here is what is **actually implemented** vs. what is **not implemented**:

### 1. Actually Implemented Protections

#### A. Input Validation and Regex Sanitization
* All Bitcoin addresses are checked against strict regexes (`RE_BITCOIN_LEGACY_P2PKH`, `RE_BITCOIN_BECH32`, `RE_BITCOIN_P2SH`) in `backend/app/core/security.py`.
* Transaction IDs and SHA-256 digests must match `^[0-9a-fA-F]{64}$`.
* Freeform text inputs pass through `sanitize_input_text()`, which strips raw HTML tags (`<[^>]*?>`) and applies `html.escape()` to prevent Cross-Site Scripting (XSS).

#### B. DoS Protection (Request Body Size Limiting)
* `RequestSizeLimitMiddleware` in `backend/app/core/security.py` inspects the HTTP `Content-Length` header on every incoming request.
* If a payload exceeds **10 MB**, it immediately aborts with `HTTP 413 Payload Too Large`.

#### C. In-Memory Sliding-Window Rate Limiting
* `RateLimiterMiddleware` in `backend/app/core/security.py` tracks request timestamps per client IP.
* Restricts automated bot abuse while exempting internal health checks and local student tests (`127.0.0.1`).

#### D. OWASP Defense-in-Depth HTTP Security Headers
* `SecurityHeadersMiddleware` appends five mandatory security headers to all responses:
  * `X-Content-Type-Options: nosniff` (prevents MIME-confusion attacks).
  * `X-Frame-Options: DENY` (prevents clickjacking and UI redressing).
  * `X-XSS-Protection: 1; mode=block` (legacy XSS filtering).
  * `Referrer-Policy: strict-origin-when-cross-origin` (protects query parameter leakage).
  * `Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()`.
  * `Cache-Control: no-store, no-cache, must-revalidate` (protects forensic investigation privacy).

#### E. SQL Injection Safety
* All database queries use **SQLAlchemy ORM** parameterization (`db.query().filter(...)`).
* No raw string concatenation is used in user queries, preventing SQL injection vulnerabilities.

#### F. Safe Global Exception Handlers
* Unexpected internal errors are caught by `unhandled_exception_handler` in `backend/app/main.py`.
* A random UUID tracking ID is generated and logged internally, and a clean generic message is returned. **No internal Python tracebacks or code snippets are ever leaked to the client.**

### 2. Explicitly NOT Implemented (Future Scope)
* ❌ User Authentication & Role-Based Access Control (RBAC): There is currently no JWT login, password system, or multi-user authentication (designed for open academic demonstration).
* ❌ HTTPS / TLS Termination: Handled at the reverse proxy (Nginx) level in production; not built into the local development server.

---

# PART 21 — COMPLETE CODE EXPLANATION

This section covers the core backend service files, explaining their purpose, key functions, and viva-relevant concepts.

### 1. `backend/app/services/mempool_client.py`
* **Purpose:** Asynchronous HTTP communication with the public Mempool API and cryptographic address validation.
* **Important Functions:**
  * `validate_bitcoin_address(address: str) -> Dict[str, Any]`: Checks address prefixes (`1`, `3`, `bc1q`, `bc1p`), Base58Check byte lengths, and Bech32 character sets.
  * `get_address_summary(address: str) -> Dict[str, Any]`: Calls `/api/address/{address}` to fetch balances and counts.
  * `get_address_transactions(address: str) -> List[Dict[str, Any]]`: Calls `/api/address/{address}/txs` to fetch transactions.
* **Key Concept:** Handles network timeouts (15s) and rate limits gracefully.

### 2. `backend/app/services/blockchain_service.py`
* **Purpose:** Central coordinator for blockchain ingestion, Satoshis-to-BTC math, and demonstration mode routing.
* **Important Functions:**
  * `sats_to_btc(sats: int) -> float`: Divides Satoshis by $100,000,000$ and rounds to 8 decimal places.
  * `normalize_tx_data(raw_tx, target_address) -> Dict`: Decomposes raw inputs and outputs into structured lists, calculates net Satoshis, and assigns flow direction (`INCOMING` vs `OUTGOING`).
  * `get_wallet_overview(address, db, case_id) -> WalletStatsResponse`: Checks if address is a synthetic demo address; if so, loads local records; otherwise queries live Mempool API.

### 3. `backend/app/services/analytics_service.py`
* **Purpose:** Calculates the 10 core observable transaction metrics.
* **Important Functions:**
  * `calculate_total_transactions()`, `calculate_incoming_transactions()`, `calculate_outgoing_transactions()`.
  * `calculate_total_received()`, `calculate_total_sent()`.
  * `calculate_average_transaction_amount()`, `calculate_largest_transaction()`, `calculate_smallest_transaction()`.
  * `calculate_unique_counterparties()`: Returns count and list of external counterparties.
  * `calculate_average_time_between_tx_hours()`: Computes mean time deltas in hours.

### 4. `backend/app/services/graph_service.py`
* **Purpose:** Assembles the directed cryptocurrency fund-flow graph.
* **Important Functions:**
  * `build_fund_flow_graph(target_address, db, depth=1, max_nodes=50) -> FundFlowGraphResponse`: Initializes NetworkX `DiGraph`, adds target node at depth 0, adds external counterparties at depth 1, creates directed transaction edges, and computes graph density.

### 5. `backend/app/services/ml_service.py`
* **Purpose:** Unsupervised anomaly detection engine using scikit-learn Isolation Forest.
* **Important Functions:**
  * `extract_features(txs, target_address) -> Dict[str, float]`: Extracts the 7 behavioral features.
  * `score_wallet(txs, wallet_address) -> (raw_score, normalized_score, classification, is_anomaly)`: Trains `IsolationForest(n_estimators=100, contamination=0.15)` and evaluates path length.
  * `analyze_wallet(...) -> MLAnalysisResponse`: Persists scan record in database and returns feature breakdown with explanations.

### 6. `backend/app/services/risk_service.py`
* **Purpose:** Transparent 0–100 investigative risk scoring.
* **Important Functions:**
  * `calculate_simple_risk_score(...) -> Dict`: Evaluates the 5 indicators (Frequency [20], Variation [15], Counterparties [20], Velocity [20], ML Anomaly [25]).
  * `determine_risk_level(score: float) -> str`: Maps 0–100 score to `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
  * `assess_wallet(...) -> RiskAssessmentResponse`: Persists assessment in SQLite and returns factors.

### 7. `backend/app/services/evidence_service.py`
* **Purpose:** Digital evidence preservation, canonicalization, SHA-256 hashing, and Chain of Custody tracking.
* **Important Functions:**
  * `create_canonical_representation(...) -> bytes`: Formats data into deterministic JSON bytes (RFC 8785).
  * `generate_evidence_hash(...) -> str`: Computes SHA-256 hash using `hashlib.sha256()`.
  * `verify_evidence_hash(...) -> (bool, str, str)`: Re-computes hash from current data and compares with stored fingerprint.
  * `preserve_transaction(...) -> SimpleEvidenceRecord`: High-level workflow saving evidence and initial custody logs.

### 8. `backend/app/services/report_service.py`
* **Purpose:** ReportLab Platypus PDF report compilation.
* **Important Functions:**
  * `generate_pdf_report(db, case_id) -> bytes`: Compiles the 13-section PDF document.
  * `NumberedCanvas`: Custom ReportLab canvas for dynamic "Page X of Y" footers.

---

# PART 22 — COMPLETE END-TO-END DEMONSTRATION WALKTHROUGH

Here is a fictional, synthetic demonstration example students can memorize and walk through during their viva defense:

### Case Profile
* **Case ID:** `CASE-DEMO-SYNTHETIC-001`
* **Title:** Apex Global Logistics Ransomware Incident
* **Incident Type:** Simulated Extortion Analysis
* **Investigator:** Cyber Defense Division
* **Investigated Wallet Address:** `1DemoRansomCollectionWallet002`

---

### Step 1: Wallet Lookup & Ingestion
The investigator inputs `1DemoRansomCollectionWallet002` into the Ingestion Console.
* Address Validation: Matches Legacy P2PKH regex (starts with `1`, valid Base58 characters).
* Mode Router: Recognized as demonstration synthetic address $\rightarrow$ loads local SQLite benchmark dataset.
* **Observed Metrics:**
  * Total Transactions: **2**
  * Total Received: **3.50 BTC** (350,000,000 Satoshis)
  * Total Sent: **3.50 BTC** (350,000,000 Satoshis)
  * Current Balance: **0.00 BTC** (fully liquidated/peeled)

---

### Step 2: Observed Transactions
1. **Transaction 1 (`demo_tx_001_synthetic_victim_payment_3_5btc`):**
   * Direction: `INCOMING`
   * Sender: `1DemoVictimCorpSimulatedDeposit001`
   * Receiver: `1DemoRansomCollectionWallet002`
   * Amount: `3.50 BTC`
   * Block Time: `2026-10-05 10:00:00 UTC`
2. **Transaction 2 (`demo_tx_002_synthetic_peeling_hop_3_49btc`):**
   * Direction: `OUTGOING`
   * Sender: `1DemoRansomCollectionWallet002`
   * Receiver: `1DemoIntermediaryHopPeeling003`
   * Amount: `3.49 BTC` (with `0.01 BTC` fee/peel)
   * Block Time: `2026-10-05 10:45:00 UTC`

---

### Step 3: Transaction Behavioral Analytics
* Inflow Count: 1
* Outflow Count: 1
* Average Transaction Amount: $\frac{3.50 + 3.49}{2} = \mathbf{3.495\text{ BTC}}$
* Unique Counterparties: **2** (`1DemoVictimCorp...`, `1DemoIntermediary...`)
* Average Time Delta: $45\text{ minutes} = \mathbf{0.75\text{ hours}}$ (rapid pass-through)

---

### Step 4: Fund-Flow Graph Construction
* **Target Node:** `1DemoRansomCollectionWallet002` (depth 0)
* **Inflow Node:** `1DemoVictimCorpSimulatedDeposit001` (depth 1)
* **Outflow Node:** `1DemoIntermediaryHopPeeling003` (depth 1)
* **Edges:**
  * $\text{Victim} \xrightarrow{\text{TX1: 3.50 BTC}} \text{Target Wallet}$
  * $\text{Target Wallet} \xrightarrow{\text{TX2: 3.49 BTC}} \text{Intermediary Hop}$

---

### Step 5: Feature Extraction & Isolation Forest Scoring
* **Extracted Feature Vector:**
  * `transaction_count`: $2.0$
  * `average_transaction_amount`: $3.495$
  * `incoming_count`: $1.0$
  * `outgoing_count`: $1.0$
  * `unique_counterparties`: $2.0$
  * `transaction_frequency`: $2.0\text{ tx/day}$
  * `amount_variance`: $0.000025$
* **Isolation Forest Execution:**
  * High average amount ($3.495\text{ BTC}$ vs baseline $0.05\text{ BTC}$) and high velocity ($0.75\text{ hrs}$) trigger fast tree isolation.
  * Raw Score: $-0.1240$
  * Normalized Score: $50.0 - (-0.1240 \times 125.0) = \mathbf{65.5}$
  * Classification: **`MEDIUM ANOMALY`**

---

### Step 6: 5-Indicator Risk Scoring
1. Frequency: 2 transactions $\rightarrow$ **0.0 pts**
2. Variance: Minimal $\rightarrow$ **0.0 pts**
3. Counterparties: 2 counterparties $\rightarrow$ **+6.0 pts**
4. Velocity: $0.75\text{ hrs}$ between txs ($\le 1.0\text{ hr}$) $\rightarrow$ **+20.0 pts**
5. ML Contribution: $\frac{65.5}{100.0} \times 25.0 = \mathbf{+16.4\text{ pts}}$
* **Total Score:** $0.0 + 0.0 + 6.0 + 20.0 + 16.4 = \mathbf{42.4}$
* **Risk Tier:** **`MEDIUM`** ($30.0$ to $59.9$)

---

### Step 7: Digital Evidence Preservation & SHA-256
Investigator preserves Transaction 1 as digital evidence:
* **Canonical Dictionary Formatted:**
  ```json
  {"amount":3.5,"case_id":"CASE-DEMO-SYNTHETIC-001","source":"Public Bitcoin Blockchain / Mempool API","timestamp":"2026-10-05 10:00:00 UTC","transaction_id":"demo_tx_001_synthetic_victim_payment_3_5btc","wallet_address":"1DemoRansomCollectionWallet002"}
  ```
* **Python `hashlib.sha256()` Digest:**
  `7f9c21b4a8e9d301c2b5e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8`
* **Evidence Record Created:** UUID `e8a1f2b3-c4d5-4e6f-8a9b-0c1d2e3f4a5b`

---

### Step 8: Chain of Custody Logging
1. `COLLECTED` — Actor: `Lead Forensic Examiner`
2. `HASHED` — Actor: `Python hashlib Engine`
3. `STORED` — Actor: `Evidence Vault Subsystem`

---

### Step 9: Court-Admissible PDF Report Generation
Investigator navigates to `/reports` and downloads `RansomTrace_Forensic_Report_CASE_DEMO_SYNTHETIC_001.pdf`.
* ReportLab renders all 13 sections.
* Section 65B Certificate attached with automated date, computer identifier, and investigator signature block.

---

# PART 23 — SYLLABUS MAPPING

This table explicitly maps RansomTrace to standard undergraduate **Cybersecurity & Cyber Forensics Course Modules (1 through 5)**:

| Course Module | Core Syllabus Topic | Corresponding RansomTrace Feature | Implementation Code / File | How to Explain in Viva Exam |
| :--- | :--- | :--- | :--- | :--- |
| **Module 1: Understanding Cyber Crime** | • Categories of Cyber Crime<br>• Ransomware mechanics & history<br>• Real-world case studies | • Ransomware incident classification<br>• WannaCry & simulated incident benchmarks | • `data/sample_cases/wannacry_sample.json`<br>• `backend/app/services/data_layer.py` (`load_demo_data`) | *"We modeled real-world ransomware payment collection mechanisms based on the 2017 WannaCry outbreak and contemporary RaaS payment patterns."* |
| **Module 2: Life Cycle of Cyber Crime** | • Reconnaissance & initial access<br>• Incident response lifecycles<br>• Fund laundering & money trails | • Multi-hop fund tracking<br>• Inflow/outflow segregation<br>• Counterparty discovery | • `backend/app/services/blockchain_service.py`<br>• `backend/app/services/analytics_service.py` | *"RansomTrace addresses the post-incident lifecycle: tracing how attackers move extortion proceeds away from initial collection wallets to obfuscate the trail."* |
| **Module 3: Legal Perspectives in Cyber Forensics** | • Cyber law fundamentals<br>• Indian IT Act 2000 (Section 65B)<br>• Privacy & DPDP Act 2023 | • Section 65B IT Act Certificate<br>• Strict privacy-by-design (zero PII storage)<br>• Standardized legal disclaimers | • `backend/app/services/report_service.py` (Section 13)<br>• `backend/app/core/security.py` | *"Electronic records must comply with Section 65B of the Indian Evidence Act / IT Act 2000. Our system automatically embeds this statutory certificate into every PDF report."* |
| **Module 4: Understanding Computer Forensics** | • Digital evidence lifecycle<br>• Chain of Custody (CoC)<br>• Tamper-proofing & integrity | • RFC 8785 canonical serialization<br>• SHA-256 fingerprinting<br>• Append-only, immutable CoC log | • `backend/app/services/evidence_service.py`<br>• `backend/app/models/custody.py`<br>• `backend/app/api/v1/evidence.py` | *"We implemented ISO/IEC 27037 standards using Python's hashlib to generate canonical SHA-256 hashes, with an append-only audit trail where edits are blocked by HTTP 403 Forbidden."* |
| **Module 5: Role of AI in Cybersecurity** | • AI in defensive cybersecurity<br>• Unsupervised machine learning<br>• Anomaly & outlier detection | • Scikit-learn Isolation Forest<br>• 7 behavioral UTXO features<br>• Tree path isolation heuristic | • `backend/app/services/ml_service.py`<br>• `backend/app/schemas/ml.py` | *"Rather than attempting impossible ransomware classification, we apply Isolation Forest to detect statistical transaction anomalies based on tree path isolation lengths."* |

---

# PART 24 — VIVA QUESTIONS & ANSWERS (75 QUESTIONS)

---

### SECTION A: BASIC QUESTIONS (Questions 1 to 25)

#### Q1: What is RansomTrace?
* **Short Answer:** An open-source digital forensics platform for tracing and analyzing Bitcoin ransomware payments using machine learning and evidence integrity preservation.
* **Detailed Answer:** RansomTrace is an investigation workbench that connects to the public Bitcoin blockchain, normalizes transaction flows, computes behavioral metrics, constructs directed fund-flow graphs, performs unsupervised anomaly detection using Isolation Forest, and generates court-admissible PDF reports compliant with Section 65B of the Indian IT Act 2000.

#### Q2: What is ransomware?
* **Short Answer:** Malicious software that encrypts a victim's files and demands payment in cryptocurrency to restore access.
* **Detailed Answer:** Ransomware is a form of malware that leverages strong asymmetric/symmetric encryption (e.g., AES-256, RSA-2048) to lock organizational data and systems. Threat actors demand payment in cryptocurrency like Bitcoin in exchange for a decryption key, often employing "double-extortion" by threatening to publish stolen data.

#### Q3: Why do ransomware extortionists prefer Bitcoin?
* **Short Answer:** Bitcoin is pseudonymous, decentralized, borderless, and transactions cannot be reversed or frozen by central banks.
* **Detailed Answer:** Unlike traditional banking networks that require identity verification (KYC) and can freeze accounts, Bitcoin operates on a peer-to-peer network without centralized control. It offers global liquidity and irreversible transactions, allowing extortionists to receive funds from anywhere in the world.

#### Q4: Is Bitcoin anonymous?
* **Short Answer:** No, Bitcoin is pseudonymous.
* **Detailed Answer:** Bitcoin does not use names, but every transaction is permanently recorded on a public, transparent ledger. If a wallet address is linked to an individual (e.g., when cashing out at a KYC-regulated exchange), their entire transaction history becomes traceable.

#### Q5: What is a Satoshi?
* **Short Answer:** The smallest unit of Bitcoin ($1\text{ BTC} = 100,000,000\text{ Satoshis}$).
* **Detailed Answer:** Named after Satoshi Nakamoto, one Satoshi equals $10^{-8}$ Bitcoins. Using Satoshis prevents floating-point rounding errors in software systems like RansomTrace.

#### Q6: What is a transaction hash (TXID)?
* **Short Answer:** A 64-character hexadecimal string uniquely identifying a Bitcoin transaction.
* **Detailed Answer:** A TXID is generated by double-SHA-256 hashing the raw binary serialization of a transaction. It serves as an immutable global identifier on the public ledger.

#### Q7: What are inputs and outputs in Bitcoin?
* **Short Answer:** Inputs are where funds come from; outputs are where funds are sent.
* **Detailed Answer:** Bitcoin uses the UTXO model. Inputs (`vin`) reference unspent outputs from prior transactions, while outputs (`vout`) specify the recipient addresses and amounts for the new transaction.

#### Q8: What is a UTXO?
* **Short Answer:** Unspent Transaction Output.
* **Detailed Answer:** A chunk of Bitcoin that has been received by an address and has not yet been spent. A user's wallet balance is the sum of all UTXOs their private keys can unlock.

#### Q9: What backend framework is used in RansomTrace?
* **Short Answer:** Python FastAPI running on Uvicorn.
* **Detailed Answer:** FastAPI is an asynchronous, high-performance web framework chosen for its native async support, automated OpenAPI (Swagger) documentation, and Pydantic data validation.

#### Q10: What frontend framework is used?
* **Short Answer:** Next.js 16 (React 19) with TypeScript and Tailwind CSS.
* **Detailed Answer:** Next.js provides the App Router architecture, rendering the Security Operations Center (SOC) dashboard, interactive charts (Recharts), and network graph visualizations (D3.js).

#### Q11: What database is used in the project?
* **Short Answer:** SQLite by default; PostgreSQL via Docker.
* **Detailed Answer:** RansomTrace uses SQLAlchemy 2.0 ORM, making it database-agnostic. It defaults to a local SQLite database (`ransomtrace.db`) for instant zero-configuration student execution.

#### Q12: What external blockchain API does RansomTrace call?
* **Short Answer:** The Mempool API (`https://mempool.space/api`).
* **Detailed Answer:** RansomTrace queries public endpoints to fetch address balances, historical transactions, and transaction details without needing to run a 600 GB local Bitcoin full node.

#### Q13: What happens if there is no internet connection during a project demonstration?
* **Short Answer:** The application seamlessly falls back to Demonstration Mode using preloaded synthetic and benchmark cases.
* **Detailed Answer:** The codebase detects synthetic demo addresses (e.g., `1Demo...` or the WannaCry benchmark) and retrieves local forensic records directly from SQLite without making external network calls.

#### Q14: What is a directed graph?
* **Short Answer:** A network of nodes connected by edges that have a defined direction (arrows).
* **Detailed Answer:** In RansomTrace, nodes represent Bitcoin wallet addresses, and directed edges represent transactions carrying funds from a sender to a receiver.

#### Q15: What Python library builds the fund-flow graph?
* **Short Answer:** NetworkX (`networkx.DiGraph`).
* **Detailed Answer:** NetworkX models the transaction graph, computes topological metrics (density, node degree), and prepares structured data for frontend rendering.

#### Q16: What machine learning algorithm is used?
* **Short Answer:** Isolation Forest from scikit-learn.
* **Detailed Answer:** An unsupervised ensemble algorithm that isolates anomalies in transaction behavioral patterns by building randomized decision trees.

#### Q17: Is Isolation Forest supervised or unsupervised?
* **Short Answer:** Unsupervised.
* **Detailed Answer:** It does not require labeled training data (it does not require a prior dataset of "ransomware" vs. "benign" labels). It identifies statistical outliers based on path length isolation.

#### Q18: What is the risk score range in RansomTrace?
* **Short Answer:** 0 to 100.
* **Detailed Answer:** The risk score evaluates 5 observable indicators, categorizing wallets into four tiers: `LOW` (0–29), `MEDIUM` (30–59), `HIGH` (60–79), and `CRITICAL` (80–100).

#### Q19: What is digital evidence?
* **Short Answer:** Any probative information stored or transmitted in digital format that can be used in a legal proceeding.
* **Detailed Answer:** In RansomTrace, digital evidence includes raw blockchain transactions, wallet findings, and forensic snapshots acquired from the public ledger.

#### Q20: What is SHA-256?
* **Short Answer:** A cryptographic hash function that outputs a 256-bit (64-character hexadecimal) digest.
* **Detailed Answer:** Developed by NIST/NSA, SHA-256 is a deterministic, one-way hash function used to verify digital evidence integrity and detect tampering.

#### Q21: What is Chain of Custody?
* **Short Answer:** A chronological, verifiable log tracking who collected, handled, and analyzed evidence.
* **Detailed Answer:** It provides a tamper-evident audit trail showing every action performed on an evidence item (`COLLECTED`, `HASHED`, `STORED`, `VERIFIED`), ensuring legal admissibility.

#### Q22: What library generates the PDF forensic report?
* **Short Answer:** ReportLab Platypus.
* **Detailed Answer:** A programmatic Python PDF publishing framework that dynamically compiles the 13-section report, tables, and Section 65B legal certificate.

#### Q23: What is Section 65B of the Indian IT Act / Evidence Act?
* **Short Answer:** A statutory certificate required by Indian courts to admit computerized electronic records into evidence.
* **Detailed Answer:** It certifies that the computer system producing the printout was operating properly and that the data was captured during lawful, regular use without tampering.

#### Q24: What is the difference between Legacy and SegWit Bitcoin addresses?
* **Short Answer:** Legacy addresses start with `1`; SegWit addresses start with `bc1`.
* **Detailed Answer:** Legacy addresses use Pay-to-PubKey-Hash (P2PKH). Native SegWit (Bech32) addresses separate witness signatures from transaction data, reducing fees and preventing transaction malleability.

#### Q25: Can RansomTrace decrypt ransomware-encrypted files?
* **Short Answer:** No.
* **Detailed Answer:** RansomTrace is a financial forensics platform that traces extortion payments on the blockchain. Decrypting encrypted files requires the attacker's private decryption key or finding implementation flaws in the malware binary.

---

### SECTION B: INTERMEDIATE QUESTIONS (Questions 26 to 50)

#### Q26: How does RansomTrace normalize transaction data?
* **Short Answer:** It converts Satoshis to Bitcoins, formats timestamps to ISO UTC, and assigns flow direction relative to the target address.
* **Detailed Answer:** In `backend/app/services/blockchain_service.py` (`normalize_tx_data`), the system parses inputs and outputs, calculates net value transferred, formats block time into human-readable UTC strings, and determines whether the transaction is `INCOMING` or `OUTGOING`.

#### Q27: How does RansomTrace determine if a transaction is INCOMING or OUTGOING?
* **Short Answer:** By checking if the investigated address appears in the inputs or outputs.
* **Detailed Answer:** If the address is present in the outputs but not inputs, it is `INCOMING` (deposit). If present in the inputs but not outputs, it is `OUTGOING` (withdrawal). If present in both, it is `INTERNAL`.

#### Q28: What is a peeling chain?
* **Short Answer:** A laundering technique where an attacker repeatedly peels off small amounts while sending the bulk change to a new address.
* **Detailed Answer:** Extortionists avoid moving entire lump sums at once. A peeling chain takes a large input, sends a small portion to a mixer or exchange, and sends the remaining balance to a newly generated change address, repeating this process across dozens of hops.

#### Q29: What graph depth is implemented in RansomTrace, and why?
* **Short Answer:** Strictly Depth 1 (direct neighbors).
* **Detailed Answer:** Depth 1 models the target wallet, its direct inflow senders, and its direct outflow recipients. Recursive multi-hop crawling (Depth 2+) causes exponential graph explosion, rapidly hitting API rate limits and freezing the system.

#### Q30: What are the 7 features extracted for the Isolation Forest model?
* **Short Answer:** Transaction count, average amount, incoming count, outgoing count, unique counterparties, transaction frequency, and amount variance.
* **Detailed Answer:** In `backend/app/services/ml_service.py` (`extract_features`), these 7 behavioral metrics capture transaction volume, velocity, dispersion, and counterparty interaction patterns without requiring manual labeling.

#### Q31: How does Isolation Forest detect anomalies?
* **Short Answer:** Anomalies are isolated near the root of random decision trees, resulting in short path lengths.
* **Detailed Answer:** Because anomalies are few and attribute-different, random partitioning splits them away from the rest of the dataset with very few cuts. Normal points require many cuts to isolate. The model computes average path length across 100 trees to calculate the anomaly score.

#### Q32: What does a negative raw score mean in scikit-learn's Isolation Forest?
* **Short Answer:** It indicates an anomaly (outlier).
* **Detailed Answer:** In scikit-learn's `decision_function()`, negative scores indicate that the instance had an average path length shorter than the expected threshold $c(n)$, signifying that it was isolated quickly.

#### Q33: How does RansomTrace calibrate the raw Isolation Forest score to a 0–100 scale?
* **Short Answer:** Using the linear transformation formula: $\text{np.clip}(50.0 - (\text{raw\_score} \times 125.0), 5.0, 95.0)$.
* **Detailed Answer:** This inverts and scales the raw score so that negative outliers translate into higher risk numbers (e.g., raw score $-0.20 \rightarrow 75.0$), clamped between 5.0 and 95.0 to avoid absolute 0% or 100% claims.

#### Q34: What are the 5 indicators that make up the 0–100 Risk Score?
* **Short Answer:** Transaction frequency (20), Amount variation (15), Counterparties (20), Rapid movement (20), and ML anomaly score (25).
* **Detailed Answer:** In `backend/app/services/risk_service.py`, each indicator evaluates observable behavioral rules, summing to a maximum of 100 points, categorized into `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL`.

#### Q35: What happens if ML analysis is unavailable or disabled during risk scoring?
* **Short Answer:** The system falls back to rule-based scoring, normalizing the 75 behavioral rule points to a 100-point scale.
* **Detailed Answer:** If transactions are missing or the ML service is disabled, the behavioral points are multiplied by $\frac{100}{75}$, setting `rule_weight = 1.0` and `ml_weight = 0.0`.

#### Q36: What is canonical serialization, and why is it required for evidence hashing?
* **Short Answer:** Ensuring JSON keys are sorted and whitespace removed so identical data always produces the identical SHA-256 hash.
* **Detailed Answer:** Standard JSON formatting does not guarantee key order or spacing. RansomTrace applies RFC 8785 principles (`json.dumps(..., sort_keys=True, separators=(",", ":"))`) to ensure deterministic byte representation before hashing.

#### Q37: How does RansomTrace verify evidence integrity?
* **Short Answer:** It re-serializes the stored data, recomputes the SHA-256 hash using `hashlib`, and compares it to the original stored hash.
* **Detailed Answer:** If the recomputed hash matches the stored fingerprint, it returns `INTEGRITY VERIFIED`. If a single character was altered, the hashes mismatch and it returns `INTEGRITY CHECK FAILED`.

#### Q38: How does the system prevent tampering with Chain of Custody records?
* **Short Answer:** Custody entries are strictly append-only; HTTP PUT and PATCH requests are blocked with HTTP 403 Forbidden.
* **Detailed Answer:** In `backend/app/api/v1/evidence.py`, routes for modifying or updating existing custody records raise an explicit `403 Forbidden` exception. New actions can only be appended to the end of the log.

#### Q39: What is the purpose of `NumberedCanvas` in the report generator?
* **Short Answer:** To dynamically calculate and display total page counts ("Page X of Y") in the footer.
* **Detailed Answer:** ReportLab cannot predict total pages during a single rendering pass. `NumberedCanvas` performs a two-pass render: recording pages in memory during pass 1, then stamping "Page X of Y" and running headers during pass 2.

#### Q40: What security middleware is implemented in the FastAPI backend?
* **Short Answer:** Request size limiting (10MB), sliding-window rate limiting, OWASP security headers, and CORS restrictions.
* **Detailed Answer:** Implemented in `backend/app/core/security.py`: `RequestSizeLimitMiddleware` prevents memory exhaustion DoS; `RateLimiterMiddleware` protects against brute-force scraping; `SecurityHeadersMiddleware` injects headers like `X-Frame-Options` and `X-Content-Type-Options`.

#### Q41: How does RansomTrace sanitize user inputs to prevent XSS?
* **Short Answer:** By stripping raw HTML tags using regex and escaping special entities with Python's `html.escape()`.
* **Detailed Answer:** In `backend/app/core/security.py` (`sanitize_input_text`), inputs are cleaned using `re.compile(r"<[^>]*?>").sub("", text)` and passed through `html.escape()` up to a maximum length boundary.

#### Q42: What is the difference between Base58Check and Bech32?
* **Short Answer:** Base58Check is used for Legacy Bitcoin addresses; Bech32 is used for native SegWit addresses.
* **Detailed Answer:** Base58 avoids ambiguous characters (0, O, I, l) and includes a 4-byte checksum. Bech32 is an alphanumeric format (using only lowercase letters and numbers) with built-in error detection based on BCH codes.

#### Q43: How does the analytics engine calculate average time between transactions?
* **Short Answer:** It sorts confirmed transaction timestamps, calculates intervals between successive transactions, and averages them into hours.
* **Detailed Answer:** In `backend/app/services/analytics_service.py` (`calculate_average_time_between_tx_hours`), successive block times $t_{i+1} - t_i$ are summed, divided by the number of intervals, and converted to hours ($\frac{\text{seconds}}{3600}$).

#### Q44: What are "activity bursts" in the analytics engine?
* **Short Answer:** Clusters of transactions occurring within 60 minutes of each other.
* **Detailed Answer:** In `build_activity_bursts()`, the system groups transactions whose timestamps are $\le 3600\text{ seconds}$ apart. Bursts of 2 or more transactions highlight automated script activity or rapid disbursement.

#### Q45: How does the system handle database migrations?
* **Short Answer:** Using Alembic version scripts.
* **Detailed Answer:** Alembic tracks incremental schema modifications (e.g., adding evidence columns or forensic tables) in `backend/alembic/versions/`, allowing database upgrades without data loss.

#### Q46: What happens if an investigated Bitcoin address has 0 transactions?
* **Short Answer:** The system returns clean zero-value metrics and an explicit message: "Insufficient transaction data for anomaly analysis."
* **Detailed Answer:** Rather than throwing division-by-zero errors or displaying empty screens, the analytics and ML engines catch empty lists and return safe default responses explaining that at least 1 transaction is required.

#### Q47: Why does the system use integer Satoshis in database storage?
* **Short Answer:** To avoid floating-point rounding errors inherent in IEEE 754 decimal arithmetic.
* **Detailed Answer:** Storing fractional Bitcoins as floats leads to precision errors (e.g. $0.1 + 0.2 = 0.30000000000000004$). Storing integer Satoshis guarantees 100% mathematical precision across all accounting operations.

#### Q48: How are external counterparties identified in a transaction?
* **Short Answer:** Any input or output address that is not equal to the investigated target wallet address is an external counterparty.
* **Detailed Answer:** In `calculate_unique_counterparties()`, inputs are tagged as senders to the wallet, outputs are tagged as recipients from the wallet, and counterparties appearing in both are tagged as `BOTH`.

#### Q49: What is the significance of the 600-profile baseline corpus in the ML service?
* **Short Answer:** It provides a stable reference distribution of typical personal wallet behaviors for the Isolation Forest model.
* **Detailed Answer:** Because unsupervised models need a reference distribution to measure isolation paths against, `BASELINE_CORPUS` establishes standard transaction frequencies, amounts, and variances against which the investigated wallet is evaluated.

#### Q50: How does the frontend communicate with the backend?
* **Short Answer:** Through asynchronous REST API calls using native `fetch()` wrapped in `frontend/src/lib/api.ts`.
* **Detailed Answer:** The Next.js frontend sends JSON requests to `http://localhost:8000/api/v1/...`, handling responses with TypeScript type safety matching backend Pydantic models.

---

### SECTION C: DIFFICULT & VIVA TRAP QUESTIONS (Questions 51 to 75)

#### Q51: How do you know this wallet actually belongs to a ransomware attacker?
* **Technically Honest Answer:** We do **not** know definitively from the blockchain alone. Bitcoin addresses are pseudonymous hashes. The wallet address is identified as suspicious because it was specified in a physical ransom note or seized malware configuration file. RansomTrace analyzes the public transaction behavior of that address, but proving real-world ownership requires subpoenas to KYC-regulated cryptocurrency exchanges.

#### Q52: Can blockchain transactions prove criminal guilt in court?
* **Technically Honest Answer:** No. Blockchain transactions prove that funds moved from Address A to Address B at a specific time. They do not prove *who* pressed the keyboard or the criminal intent behind the transfer. RansomTrace provides investigative indicators and evidence preservation, not judicial verdicts.

#### Q53: Why did you choose Isolation Forest over Random Forest?
* **Technically Honest Answer:** Random Forest is a **supervised classification** algorithm that requires thousands of pre-labeled training examples ($y = \text{Ransomware}$ vs $y = \text{Benign}$). In cryptocurrency forensics, verified ground-truth labels for ransomware wallets are sparse and constantly outdated. Isolation Forest is an **unsupervised anomaly detection** algorithm that identifies statistical outliers without requiring training labels.

#### Q54: Why not use a supervised Deep Learning model (like LSTM or GNN)?
* **Technically Honest Answer:** Deep learning models require massive labeled datasets and act as unexplainable black boxes. In digital forensics, court admissibility demands explainability. If an AI flags a wallet, the investigator must be able to explain *why* (e.g., path length, high velocity, high variance) to a judge. Isolation Forest combined with transparent heuristic attribution provides full explainability.

#### Q55: What is the mathematical difference between anomaly detection and classification?
* **Technically Honest Answer:** Classification learns a decision boundary separating two or more known classes based on labeled training data: $f(X) \to Y$. Anomaly detection models the baseline distribution of data points and calculates a continuous divergence or path length score $s(x)$ measuring how far an instance deviates from expected normalcy: $f(X) \to \mathbb{R}$.

#### Q56: Can SHA-256 be reversed or cracked?
* **Technically Honest Answer:** No. SHA-256 is a one-way mathematical function. Finding an original input from a hash requires brute-force guessing. With $2^{256}$ possible combinations, reversing SHA-256 would require more energy than exists in the observable universe. There are no known practical preimage attacks against SHA-256.

#### Q57: What is a hash collision, and can it happen in SHA-256?
* **Technically Honest Answer:** A collision occurs when two distinct inputs produce the exact same hash: $H(x_1) = H(x_2)$ where $x_1 \neq x_2$. Mathematically, collisions exist by the Pigeonhole Principle. However, for SHA-256, the probability of finding a collision by chance is approximately $1 \text{ in } 2^{128}$, which is considered cryptographically impossible with current computing technology.

#### Q58: What happens if an investigator modifies an evidence record in the database?
* **Technically Honest Answer:** The next time `verify_evidence_integrity()` is executed, the recomputed canonical SHA-256 hash will not match the original stored hash. The system will flag the item as `INTEGRITY CHECK FAILED` and log a tamper alert in the Chain of Custody.

#### Q59: Is your risk score scientifically proven?
* **Technically Honest Answer:** No. The risk score is an **investigative heuristic prioritization indicator**, not a certified scientific constant. It is a weighted sum of 5 observable indicators designed to help SOC analysts prioritize which alerts to examine first. It does not claim statistical certainty.

#### Q60: What happens if the external Mempool API goes down during a real investigation?
* **Technically Honest Answer:** The system catches the HTTP timeout or connection error and automatically checks the local database cache. If the wallet was queried previously, it serves the cached forensic record. If not, the investigator can switch to preloaded benchmark cases in Demonstration Mode.

#### Q61: What is the difference between encryption and hashing?
* **Technically Honest Answer:** Hashing is a one-way mathematical operation that produces a fixed-size digest used for tamper verification; it cannot be decrypted. Encryption is a two-way operation that transforms plaintext into ciphertext using a key; it can be decrypted back to plaintext by anyone holding the corresponding key.

#### Q62: Why did you implement Depth 1 for the graph instead of Depth 2 or 3?
* **Technically Honest Answer:** Depth 1 provides direct, explainable 1-hop visibility. On a public blockchain, recursive depth exploration leads to combinatorial explosion. A single counterparty that happens to be an exchange or mining pool would introduce thousands of transactions, overwhelming memory and API rate limits. Depth 1 guarantees immediate, deterministic execution.

#### Q63: What part of this project is actually Cybersecurity?
* **Technically Honest Answer:** The operational scope addresses the post-incident phase of the cybercrime lifecycle: analyzing extortion payments resulting from malware attacks, applying OWASP defense-in-depth API protections, rate limiting, input sanitization, and investigating adversary fund laundering.

#### Q64: What part of this project is Digital Forensics?
* **Technically Honest Answer:** The acquisition of public blockchain artifacts, RFC 8785 canonical serialization, SHA-256 tamper verification, append-only Chain of Custody tracking compliant with ISO/IEC 27037, and generating court-admissible PDF reports with Section 65B Indian IT Act certificates.

#### Q65: What part of this project is Artificial Intelligence?
* **Technically Honest Answer:** The unsupervised machine learning subsystem in `ml_service.py`, which extracts 7 continuous behavioral features, fits an Isolation Forest model, measures tree path isolation lengths, and generates explainable anomaly factor attributions.

#### Q66: What are the main technical limitations of RansomTrace?
* **Technically Honest Answer:**
  1. It traces only Bitcoin (does not trace privacy coins like Monero).
  2. It relies on public APIs or demonstration datasets rather than running a self-hosted full node.
  3. It cannot de-anonymize wallet owners without off-chain KYC intelligence.
  4. Graph traversal is limited to direct depth-1 neighbors.

#### Q67: What would you improve in the future?
* **Technically Honest Answer:**
  1. Add support for Ethereum and Monero blockchains.
  2. Implement an optional self-hosted Bitcoin Core RPC node integration.
  3. Add user authentication (JWT / RBAC) for enterprise SOC teams.
  4. Integrate off-chain intelligence feeds (e.g., sanctioned entity wallet lists).

#### Q68: Why does the system use RFC 8785 canonical JSON instead of standard `json.dumps()`?
* **Technically Honest Answer:** Standard `json.dumps()` does not enforce alphabetical key sorting or whitespace rules. Two identical JSON dictionaries could serialize with different key orders or spaces, resulting in completely different SHA-256 hashes. Canonical serialization guarantees that identical data always yields the identical cryptographic hash.

#### Q69: If Bitcoin is public, why can't police simply catch ransomware attackers immediately?
* **Technically Honest Answer:** Because creating a Bitcoin wallet requires no identification. Attackers route funds through decentralized mixers (Wasabi, Tornado Cash), coin swaps, and peer-to-peer exchanges in non-cooperative jurisdictions. Tracing the funds is possible, but identifying the physical human behind the keyboard requires international law enforcement coordination and subpoenas.

#### Q70: What is transaction velocity in cryptocurrency forensics?
* **Technically Honest Answer:** Transaction velocity measures the speed and frequency with which funds are moved after being received. Human users typically hold funds for days or months. Extortionists and automated laundering scripts move funds within minutes of receipt to minimize the window for asset tracking.

#### Q71: How does your application protect itself from Cross-Site Scripting (XSS)?
* **Technically Honest Answer:** On the backend, all string inputs pass through regex tag strippers and Python's `html.escape()`. In HTTP responses, `X-XSS-Protection` and `X-Content-Type-Options: nosniff` headers are enforced. On the frontend, React automatically escapes string variables rendered in JSX.

#### Q72: How does the rate limiter work in the backend?
* **Technically Honest Answer:** `RateLimiterMiddleware` maintains an in-memory dictionary mapping client IP addresses to sliding lists of Unix timestamps. When a request arrives, timestamps older than 60 seconds are purged. If the count exceeds the limit, the server immediately returns `HTTP 429 Too Many Requests` with a `Retry-After` header.

#### Q73: Why does the database have both `wallets` and `investigation_cases` tables?
* **Technically Honest Answer:** To maintain relational integrity. A single investigation case (e.g., a corporate ransomware outbreak) may involve multiple extortion addresses, transit hops, and change wallets. `Wallet` records maintain a foreign key (`case_id`) pointing to their parent `investigation_cases` record.

#### Q74: What is the purpose of the `raw_payload` field in the `evidences` table?
* **Technically Honest Answer:** It stores the original, unmutated JSON representation of the transaction or finding at the exact moment of acquisition. This preserves the original artifact so that future forensic re-examinations can re-verify the canonical SHA-256 hash.

#### Q75: How does RansomTrace ensure that evidence is court-admissible?
* **Technically Honest Answer:** Court admissibility requires proving authenticity, integrity, and provenance. RansomTrace establishes authenticity by recording the exact blockchain source; integrity through canonical SHA-256 hashing; provenance through an append-only Chain of Custody; and statutory compliance through an automated Section 65B Indian IT Act certificate.

---

# PART 25 — BEGINNER GLOSSARY

| Term | Simple Definition | Concrete Example | How it Appears in RansomTrace |
| :--- | :--- | :--- | :--- |
| **Ransomware** | Malware that encrypts victim files and demands cryptocurrency payment. | WannaCry, LockBit, Conti. | Modeled in `InvestigationCase` and preloaded benchmark cases. |
| **Blockchain** | A decentralized, append-only public ledger of cryptographically linked blocks. | The Bitcoin network ledger. | Ingested via Mempool API into normalized data structures. |
| **Bitcoin (BTC)** | The first decentralized peer-to-peer cryptocurrency. | 1.0 BTC = 100,000,000 Satoshis. | Converted using `sats_to_btc()` across all analytics services. |
| **Wallet Address** | An alphanumeric public identifier where funds are sent. | `13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94` | Stored in `Wallet.address`; validated using Base58Check/Bech32 regex. |
| **Transaction Hash (TXID)**| 64-character hexadecimal unique identifier of a transaction. | `9f7b11c38e9d40a1b6a2...` | Stored in `Transaction.txid`; validated using `^[0-9a-fA-F]{64}$`. |
| **UTXO** | Unspent Transaction Output; spendable coins in a wallet. | An unspent 0.5 BTC output. | Decomposed into structured `TxIO` input/output objects. |
| **Input (`vin`)** | Reference to funds being spent in a transaction. | Previous transaction output unlocked by sender. | Extracted in `normalize_tx_data()` to identify sending addresses. |
| **Output (`vout`)** | Destination address and amount in a transaction. | 3.5 BTC locked to extortion wallet address. | Extracted in `normalize_tx_data()` to identify receiving addresses. |
| **Node** | An entity in a network graph representing an address. | Target wallet node or sender node. | Modeled as `GraphNode` in `backend/app/schemas/graph.py`. |
| **Edge** | A directed link in a graph representing a transaction. | Arrow from Victim $\rightarrow$ Target Wallet. | Modeled as `GraphEdge` containing TXID and BTC amount. |
| **API** | Application Programming Interface; software communication bridge. | Mempool REST API. | Queried asynchronously via `MempoolClient` in Python. |
| **Endpoint** | A specific URL where an API receives requests. | `GET /api/v1/wallets/{address}` | Defined in FastAPI router controllers (`wallets.py`). |
| **JSON** | JavaScript Object Notation; lightweight text data format. | `{"address": "1Demo...", "balance": 0}` | Standard data exchange format between backend and frontend. |
| **Feature** | An individual measurable property used by a machine learning model. | `average_transaction_amount = 0.5` | 7 features extracted in `ml_service.py` (`extract_features`). |
| **Machine Learning** | Algorithms that learn mathematical patterns directly from data. | Scikit-learn algorithms. | Applied for anomaly detection in `MLAnomalyService`. |
| **Unsupervised Learning**| Machine learning on data with zero labels or answers. | Finding unusual transaction outliers. | The execution paradigm of Isolation Forest. |
| **Anomaly Detection** | Identifying observations that deviate significantly from the baseline. | Flagging a wallet moving millions in seconds. | Classifies wallets as `NORMAL`, `LOW`, `MEDIUM`, or `HIGH ANOMALY`. |
| **Isolation Forest** | Unsupervised algorithm that isolates anomalies using random trees. | Ensemble of 100 Isolation Trees. | Instantiated in `ml_service.py` with `n_estimators=100`. |
| **Risk Score** | 0 to 100 numerical indicator prioritizing investigation urgency. | Score = 78.0 (`HIGH` tier). | Computed in `risk_service.py` across 5 observable indicators. |
| **Digital Evidence** | Electronic data of probative value stored for legal proceedings. | Preserved JSON transaction snapshot. | Stored in `Evidence` table with SHA-256 fingerprint. |
| **Forensics** | Scientific investigation methods admissible in a court of law. | ISO/IEC 27037 digital evidence handling. | Governs the entire preservation and reporting pipeline. |
| **Chain of Custody** | Chronological audit trail documenting evidence handling. | `COLLECTED` $\rightarrow$ `HASHED` $\rightarrow$ `STORED`. | Stored in `ChainOfCustodyEntry` table; immutable. |
| **Hash** | A fixed-size hexadecimal string generated by a one-way function. | `e3b0c44298fc1c149afbf4c8996fb92...` | Generated by Python standard `hashlib.sha256()`. |
| **SHA-256** | Secure Hash Algorithm producing a 256-bit digest. | Standard FIPS PUB 180-4 algorithm. | Used for all evidence hashing and tamper verification. |
| **Integrity** | Verification that data has not been modified or corrupted. | Hashes match $\rightarrow$ `INTEGRITY VERIFIED`. | Checked by `verify_evidence_integrity()` in `evidence_service.py`. |
| **Incident Response** | Coordinated methodology to manage a cyberattack. | NIST SP 800-61 lifecycle. | RansomTrace supports the post-incident containment and analysis stage. |

---

# PART 26 — WHAT STUDENTS MUST MEMORIZE FOR THE VIVA

To prepare efficiently for the project demonstration and viva exam, students should focus on these prioritized concepts:

### MUST KNOW (Absolute Minimum for Passing)
1. **The Project Purpose:** RansomTrace traces Bitcoin ransomware extortion payments, calculates 10 behavioral metrics, builds fund-flow graphs, runs unsupervised anomaly detection, and preserves court-admissible evidence with SHA-256 hashes.
2. **Why Bitcoin is Used:** It is pseudonymous, decentralized, borderless, and transactions cannot be reversed or frozen by banks.
3. **The ML Model:** We use **Isolation Forest** from scikit-learn. It is **unsupervised** anomaly detection. It isolates outliers faster than normal points (short path lengths in decision trees).
4. **Why NOT Classification:** Real-world ransomware wallets lack ground-truth labels. The goal is to detect unusual transaction behavior for triage, not to claim criminal guilt.
5. **The 5 Risk Indicators:** Frequency (20 pts), Amount Variation (15 pts), Counterparties (20 pts), Rapid Movement (20 pts), and ML Anomaly (25 pts). Sums to 100.
6. **SHA-256 & Chain of Custody:** Evidence is serialized into canonical JSON and hashed with Python `hashlib.sha256()`. Custody logs are strictly append-only; edits are blocked with HTTP 403 Forbidden.
7. **Legal Compliance:** The PDF report attaches an automated Section 65B Indian IT Act 2000 certificate for courtroom admissibility.

### SHOULD KNOW (For High Marks)
1. **The 10 Analytics Metrics:** Total tx, incoming tx, outgoing tx, total received, total sent, mean amount, largest tx, smallest tx, unique counterparties, and average time delta between transactions.
2. **Graph Implementation:** Built with NetworkX (`DiGraph`). Nodes are wallet addresses; edges are transactions. Traversal is strictly **Depth 1** (direct neighbors) to prevent combinatorial explosion.
3. **Demonstration Mode:** If the internet fails or APIs rate limit, the system serves preloaded synthetic and benchmark cases directly from SQLite.
4. **Application Security:** Request size limits (10MB), sliding-window rate limiting, OWASP security headers, and HTML tag sanitization.

### GOOD TO KNOW (For Perfection / Honors)
1. **UTXO Mechanics:** Difference between the UTXO model (inputs and outputs) and the account balance model.
2. **RFC 8785 Canonical JSON:** Alphabetical key sorting and whitespace stripping ensuring deterministic hashing.
3. **ReportLab `NumberedCanvas`:** Two-pass rendering required to calculate "Page X of Y" in PDF footers.
4. **Isolation Forest Math:** $s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$, where $c(n)$ is average path length in a binary search tree.

---

# PART 27 — FINAL PROJECT SUMMARY & 2-MINUTE ELEVATOR PITCH

### One-Page Master Summary
* **Project Name:** RansomTrace
* **Problem Statement:** Ransomware extortionists demand payments in cryptocurrency to bypass traditional banking controls. Law enforcement and incident response teams struggle to analyze transaction flows, detect behavioral anomalies, and preserve tamper-evident digital evidence compliant with court standards.
* **Objectives:**
  1. Ingest and normalize public Bitcoin transactions via REST APIs with offline fallback.
  2. Compute 10 transparent transaction behavioral metrics and construct directed fund-flow graphs.
  3. Apply unsupervised machine learning (Isolation Forest across 7 UTXO features) to detect statistical transaction anomalies.
  4. Calculate a 0–100 investigative risk score across 5 observable indicators.
  5. Preserve digital evidence using canonical JSON serialization, SHA-256 cryptographic hashing, and append-only Chain of Custody tracking.
  6. Generate court-ready PDF forensic investigation dossiers compliant with Section 65B of the Indian IT Act 2000.
* **Technology Stack:** Next.js 16 (React 19), TypeScript, Tailwind CSS v4, Recharts, D3.js, FastAPI, Pydantic, SQLAlchemy 2.0, SQLite / PostgreSQL, scikit-learn, NetworkX, ReportLab, and Python `hashlib`.
* **System Boundaries:** Exclusively analyzes public ledger data; zero PII storage; does not claim de-anonymization or legal guilt; does not execute fund transfers or crack file encryption.

---

### The 2-Minute Presentation Speech (Memorize This!)

> *"Respected Examiners and Professors, good morning.*
>
> *Today, we present **RansomTrace**, our capstone project in Cybersecurity and Digital Forensics.*
>
> *When an enterprise falls victim to a ransomware attack, the attackers demand extortion payments in Bitcoin. Because Bitcoin is decentralized and pseudonymous, traditional banking asset freezes are impossible. However, because Bitcoin's ledger is completely public and immutable, every transaction is permanently visible.*
>
> *RansomTrace provides a complete, court-compliant forensic investigation workbench:*
>
> *First, it ingests blockchain transactions using the public Mempool API, with a built-in offline Demonstration Mode to guarantee reliable execution without external network dependency.*
>
> *Second, it normalizes raw Satoshis into Bitcoins and calculates **10 core behavioral metrics**, such as transaction velocity, volume, and unique counterparty interactions.*
>
> *Third, it models fund dispersion as a **directed fund-flow graph** using NetworkX, mapping direct inflow senders and outflow recipients.*
>
> *Fourth, for artificial intelligence, we implement **Isolation Forest** from scikit-learn. Because real-world ransomware wallets lack ground-truth labels, we do not use supervised classification. Instead, we extract **7 behavioral features** and evaluate tree path isolation lengths to identify statistical outliers.*
>
> *Fifth, we combine these behavioral rules and the ML anomaly result into a transparent **0 to 100 Investigative Risk Score**, categorizing wallets into Low, Medium, High, and Critical triage tiers.*
>
> *Finally, addressing digital forensics standards under ISO/IEC 27037 and Section 65B of the Indian IT Act 2000, RansomTrace serializes evidence into canonical JSON, generates cryptographic **SHA-256 fingerprints** using Python's `hashlib`, maintains an **append-only Chain of Custody** where edits are strictly forbidden, and compiles a complete, court-admissible PDF forensic dossier using ReportLab.*
>
> *The system maintains strict ethical boundaries: it does not claim to prove criminal guilt or de-anonymize individuals; it serves as an investigative decision-support platform for cybersecurity analysts.*
>
> *Thank you. We are now ready to demonstrate the live platform and answer your questions."*

---

*End of Comprehensive Learning Guide.*
