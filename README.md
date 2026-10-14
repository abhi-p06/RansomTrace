# RansomTrace
**Cybercrime Investigation, Cryptocurrency Forensics & AI-Based Ransomware Payment Analysis Platform**  
*A B.Tech Cybersecurity Course Capstone Project*

---

## 📌 Executive Summary
**RansomTrace** is a specialized digital forensics and cryptocurrency investigation platform engineered to trace, analyze, and document ransomware extortion payments on the Bitcoin blockchain. It combines live public blockchain data ingestion, graph-based fund flow reconstruction, unsupervised machine learning anomaly detection (Isolation Forest), and digital evidence preservation compliant with **ISO/IEC 27037** and **Section 65B of the Indian Information Technology Act 2000**.

---

## 🎓 Academic Syllabus Alignment (Modules 1 – 5)

| Course Module | Syllabus Topic | RansomTrace Technical Implementation |
| :--- | :--- | :--- |
| **Module 1: Understanding Cyber Crime** | • Cybercrime categories<br>• Ransomware mechanics<br>• Real-world cases | • Ransomware incident classification (WannaCry, LockBit, DarkSide).<br>• Pre-loaded forensic case archives in `data/sample_cases/`. |
| **Module 2: Life Cycle of Cyber Crime** | • Reconnaissance<br>• Incident response lifecycle<br>• Case studies | • NIST SP 800-61 incident lifecycle tracker.<br>• Multi-hop counterparty wallet reconnaissance and fund splitting detection. |
| **Module 3: Legal Perspectives in Cyber Forensics** | • Cybercrime laws<br>• Indian IT Act 2000 (Section 65B)<br>• DPDP Act 2023 / GDPR | • Automated **Section 65B Indian IT Act 2000 Certificate** in forensic reports.<br>• Privacy-by-design architecture: strictly public ledger data, zero PII storage. |
| **Module 4: Understanding Computer Forensics** | • Digital evidence lifecycle<br>• Chain of custody (CoC)<br>• Integrity preservation | • ISO/IEC 27037 Digital Evidence Vault.<br>• RFC 8785 canonical JSON serialization & SHA-256 tamper verification.<br>• Append-only, hash-chained forensic audit trail. |
| **Module 5: Role of AI in Cybersecurity** | • Proactive/reactive defense<br>• ML in cybersecurity<br>• Anomaly detection | • Scikit-learn **Isolation Forest** model.<br>• 14 engineered UTXO behavioral heuristics (peel chains, velocity, fan-out).<br>• Transparent feature contribution explainability. |

---

## 🛠️ Architecture & Tech Stack
* **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, Lucide Icons, Cyber SOC Dark Design System.
* **Backend:** Python FastAPI, Pydantic Settings, SQLAlchemy ORM, Uvicorn.
* **Database:** Dialect-agnostic SQLAlchemy (SQLite for instant zero-config startup, PostgreSQL via Docker/production).
* **Migrations:** Alembic database versioning.
* **Blockchain Source:** Bitcoin public ledger via Mempool API.

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.11+ (Python 3.13 tested)
- Node.js 18+ & npm 9+
- (Optional) Docker & Docker Compose for PostgreSQL

---

### Step 1: Backend Setup & Launch
```bash
# 1. Navigate to project root
cd /path/to/cybersecproj

# 2. Activate virtual environment
source backend/venv/bin/activate

# 3. (Optional) Install dependencies if not already installed
pip install -r backend/requirements.txt

# 4. Run database migrations
cd backend && alembic upgrade head && cd ..

# 5. Launch FastAPI Backend
source backend/venv/bin/activate && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend API will start on **http://localhost:8000**.  
Interactive Swagger documentation is available at **http://localhost:8000/docs**.

---

### Step 2: Frontend Setup & Launch
```bash
# 1. Open a new terminal and navigate to frontend
cd /path/to/cybersecproj/frontend

# 2. (Optional) Install dependencies if not already installed
npm install

# 3. Launch Next.js Dev Server
npm run dev
```
The SOC Command Center will start on **http://localhost:3000**.

---

### Step 3: (Optional) Running with PostgreSQL via Docker
```bash
# Start PostgreSQL container
docker compose up -d

# Update .env to use PostgreSQL:
# DATABASE_URL="postgresql://ransomtrace_user:ransomtrace_password@localhost:5432/ransomtrace_db"

# Apply migrations
source backend/venv/bin/activate && cd backend && alembic upgrade head && cd ..
```

---

## 🔍 Health & Diagnostic Endpoints
- **System Health:** `GET http://localhost:8000/api/v1/health`
- **Root Status:** `GET http://localhost:8000/`
- **Interactive Swagger Docs:** `GET http://localhost:8000/docs`
- **ReDoc Technical Reference:** `GET http://localhost:8000/redoc`

---

## ⚖️ Ethical & Legal Boundary Safeguards
1. **Public Information Exclusively:** Queries only public, immutable blockchain ledger data.
2. **Strict Non-Deanonymization:** Does not de-anonymize private individuals, dox wallet owners, or harvest personal identifiable information.
3. **No Financial Transactions:** Zero wallet custody, private key handling, or fund transfers.
4. **Investigative Heuristic Indicator:** All anomaly scores are probabilistic investigative indicators and do not constitute definitive legal proof of illicit activity.
