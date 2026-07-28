# 🚀 HireSmart AI - Campus Recruitment Automation System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3--70B-f34f29.svg?style=flat)](https://groq.com/)
[![SentenceTransformers](https://img.shields.io/badge/Embeddings-Sentence--Transformers-ff6f00.svg?style=flat)](https://www.sbert.net/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**HireSmart AI** is an enterprise-grade, AI-powered Campus Recruitment Automation System. It streamlines candidate ingestion, automates resume parsing with high-performance LLMs, ranks candidates using hybrid semantic vector embeddings, generates recruitment analytics, exports customizable reports, and automates interview invitation dispatches.

---

## ✨ Key Features

- 📄 **Automated Resume Parsing**: Parses candidate resumes from PDF format using **PyMuPDF** (`fitz`) and extracts structured candidate profiles via **Groq LLaMA 3.3 70B Versatile**.
- 🤖 **UiPath & Google Drive Robot Integration**: Supports automated batch ingestion of candidate resumes directly from watch folders, UiPath Orchestrator, or cloud storage.
- 🎯 **Job Description Intelligence**: Automatically extracts required technical skills, experience metrics, soft skills, and educational qualifications from job postings.
- 🧠 **Hybrid AI Ranking Engine**: Combines **Sentence Transformers** (`all-MiniLM-L6-v2`) vector cosine similarity with **Groq LLM** reasoning for accurate candidate-job match scoring.
- 📊 **Recruitment Analytics & Funnel Insights**: Provides real-time metrics on candidate scores, top extracted skills, department distributions, and candidate qualification funnels.
- 📈 **Multi-Format Report Export**: Exports structured recruitment reports in **Excel (`.xlsx`)**, **CSV (`.csv`)**, and **JSON (`.json`)** formats.
- 📧 **Automated SMTP Email Dispatch**: Sends custom interview invitation emails to shortlisted candidates with configurable templates.
- 🔒 **Secure Authentication**: Built-in JWT bearer token authentication with Passlib bcrypt password hashing.
- 🔄 **Smart Database Fallback**: Async SQLAlchemy database layer with primary support for **MySQL** (`aiomysql`) and an automatic fallback to **SQLite** (`aiosqlite`) for zero-configuration local development.

---

## 🛠️ Tech Stack & Architecture

| Component | Technology / Library |
| :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Async ASGI) |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) |
| **Database ORM** | [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/) + [Alembic](https://alembic.sqlalchemy.org/) |
| **Primary Database** | MySQL (`aiomysql` & `pymysql`) |
| **Fallback Database** | SQLite (`aiosqlite`) |
| **LLM Engine** | [Groq API](https://groq.com/) (`llama-3.3-70b-versatile`) |
| **Vector Embeddings** | [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) + Scikit-Learn |
| **PDF Extraction** | [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) |
| **Data Export** | Pandas, OpenPyXL |
| **Authentication** | PyJWT + Passlib (bcrypt) |
| **Emailing** | `aiosmtplib` (Async SMTP) |
| **Testing** | Async HTTPX Test Suite |

---

## 📁 Repository Structure

```
HireSmart-AI/
├── .env                      # Global environment settings
├── .gitignore                # Git exclusion rules
├── requirements.txt          # Root Python dependencies
├── README.md                 # Project documentation
├── backend/
│   ├── app.py                # FastAPI app initialization, CORS, middleware & lifespan
│   ├── config.py             # Settings configuration via Pydantic BaseSettings
│   ├── database.py           # Async SQLAlchemy engine & automatic SQLite fallback
│   ├── check_db.py           # DB connection validator script
│   ├── create_mysql_db.py    # Auto-provisions MySQL database if missing
│   ├── test_backend.py       # End-to-end async HTTPX test suite
│   ├── alembic.ini           # Database migration configuration
│   ├── alembic/              # Database migration scripts
│   ├── models/               # SQLAlchemy ORM models (Recruiter, Candidate, JD, Analysis)
│   ├── schemas/              # Pydantic schemas for request/response validation
│   ├── routes/               # API endpoint routers
│   │   ├── auth.py           # Recruiter registration, login, profile (/auth)
│   │   ├── upload.py         # Resume PDF upload endpoint (/upload-resume)
│   │   ├── candidates.py     # Candidate listing and detail retrieval (/candidates)
│   │   ├── job_description.py# Job Description management (/job-description)
│   │   ├── analyze.py        # AI Candidate Ranking Engine (/analyze)
│   │   ├── analytics.py      # Recruitment analytics & funnel stats (/analytics)
│   │   ├── reports.py        # Excel/CSV/JSON report exports (/reports)
│   │   └── email.py          # SMTP Email scheduling & dispatch (/email)
│   ├── services/             # Core business logic layer
│   │   ├── auth_service.py
│   │   ├── candidate_service.py
│   │   ├── job_service.py
│   │   ├── ranking_service.py
│   │   ├── resume_service.py
│   │   ├── analytics_service.py
│   │   ├── report_service.py
│   │   └── email_service.py
│   ├── utils/                # Helper utilities (PyMuPDF parser, Groq client, embeddings)
│   ├── uploads/              # Uploaded resume PDFs & parsed JSON files
│   └── reports/              # Generated recruitment export reports
```

---

## ⚙️ Prerequisites

Before running the project, ensure you have installed:

- **Python**: `3.10` or higher
- **Groq API Key**: Obtain an API key from [Groq Console](https://console.groq.com/)
- **MySQL Server** *(Optional)*: Version 8.0+ (If MySQL is not installed or running, HireSmart AI automatically falls back to local SQLite database `backend/hiresmart_dev.db`).

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/HireSmart-AI.git
cd HireSmart-AI
```

### 2. Set Up Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration

Create or update the `.env` file inside the `backend` directory (or workspace root).

Sample `backend/.env` file:

```env
# Application Metadata
PROJECT_NAME="HireSmart AI - Campus Recruitment Automation System"
VERSION="1.0.0"
DEBUG=True

# Database Configuration (MySQL with automatic SQLite fallback)
DATABASE_URL="mysql+aiomysql://root:your_password@localhost:3306/hiresmart_db"

# JWT Security
SECRET_KEY="your_super_secret_jwt_key_here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Groq AI Service
GROQ_API_KEY="gsk_your_groq_api_key_here"
MODEL="llama-3.3-70b-versatile"

# Sentence Transformers Vector Model
EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2"

# Storage Directories
UPLOAD_DIR="uploads"
PDF_DIR="uploads/pdf"
JSON_DIR="uploads/json"
REPORT_DIR="reports"

# Email SMTP Settings (for interview invites)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="recruitment@hiresmart.ai"
SMTP_PASSWORD="your_app_password"
EMAIL_FROM="recruitment@hiresmart.ai"
```

---

## 🗄️ Database Setup

HireSmart AI supports zero-config DB startup:

1. **MySQL Setup (Recommended for Production)**:
   Run the database creation helper to provision `hiresmart_db`:
   ```bash
   cd backend
   python create_mysql_db.py
   ```
2. **SQLite Fallback (Development Default)**:
   If MySQL server credentials are not configured or connection fails, HireSmart AI automatically creates and initializes `backend/hiresmart_dev.db` using `aiosqlite`.

---

## 🏃 Running the Application

Navigate to the `backend` directory and launch the Uvicorn development server:

```bash
cd backend
python app.py
```
*Or directly via Uvicorn:*
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Once running, the backend server will be available at:
- **Base URL**: `http://localhost:8000`
- **Interactive Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Automated Tests

HireSmart AI includes a complete end-to-end async test suite using `httpx` and `asyncio`:

```bash
cd backend
python test_backend.py
```

The test suite validates:
1. Health check endpoint (`GET /`)
2. Recruiter registration, login, and JWT validation (`/auth/*`)
3. Job Description creation and retrieval (`/job-description`)
4. PDF resume upload and PyMuPDF + Groq LLM extraction (`/upload-resume`)
5. Candidate retrieval (`/candidates`)
6. Hybrid AI ranking engine execution (`POST /analyze`)
7. Recruitment analytics calculation (`GET /analytics`)
8. Multi-format report exports (Excel, CSV, JSON) & download validation (`/reports/*`)
9. Automated SMTP email dispatch (`POST /email/send-shortlisted`)

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Health check & API version | ❌ |
| `POST` | `/auth/register` | Register a new recruiter account | ❌ |
| `POST` | `/auth/login` | Authenticate recruiter & obtain JWT token | ❌ |
| `GET` | `/auth/me` | Fetch authenticated recruiter profile | Bearer Token |
| `POST` | `/job-description` | Create a new Job Description | Bearer Token |
| `GET` | `/job-descriptions` | List all created Job Descriptions | ❌ |
| `POST` | `/upload-resume` | Upload PDF resume for AI parsing & candidate creation | ❌ |
| `GET` | `/candidates` | Retrieve all parsed candidate profiles | ❌ |
| `GET` | `/candidate/{id}` | Get detailed profile of candidate by ID | ❌ |
| `POST` | `/analyze` | Run Hybrid AI ranking for candidates against a JD | ❌ |
| `GET` | `/analytics` | Retrieve recruitment metrics, skills distribution & statistics | ❌ |
| `POST` | `/reports/excel` | Generate downloadable Excel report (`.xlsx`) | ❌ |
| `POST` | `/reports/csv` | Generate downloadable CSV report (`.csv`) | ❌ |
| `POST` | `/reports/json` | Generate JSON report data | ❌ |
| `GET` | `/reports/download/{filename}` | Download generated report file | ❌ |
| `POST` | `/email/send-shortlisted` | Send interview invitation emails via SMTP | ❌ |

---

## 🤖 UiPath & Automation Integration

HireSmart AI seamlessly integrates with **UiPath Robots** and **Google Drive sync**:

1. **Watch Folder / Google Drive Ingestion**:
   UiPath robots monitor Google Drive / local folders for incoming student resumes (PDF format).
2. **Automated API Trigger**:
   When new resumes land in the input queue, UiPath dispatches HTTP requests to `POST http://localhost:8000/upload-resume`.
3. **Automated AI Processing**:
   The backend extracts text, parses candidate details using Groq LLM, updates vector embeddings, and calculates job match scores automatically.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
