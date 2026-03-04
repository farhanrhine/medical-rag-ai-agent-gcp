# 🏥 MedAssist AI — Medical RAG Chatbot

An AI-powered medical question-answering chatbot built with **LangChain Agents**, **RAG (Retrieval-Augmented Generation)**, and **Flask**. The agent retrieves verified medical information from *The GALE Encyclopedia of Medicine, 2nd Edition* and provides cited, trustworthy answers.

## 🔄 Workflow

```mermaid
flowchart TD
    A["🧑 User asks a medical question"] --> B["🌐 Flask Web Server"]
    B --> C["🤖 AI Agent"]
    C --> D["🔧 Search Medical Database"]
    D --> E["📦 FAISS Vector Store\n(pre-built from PDF)"]
    E -->|"Top 3 relevant chunks\n+ real page numbers"| C
    C --> F["💬 LLM generates short answer\nusing ONLY the retrieved text"]
    F --> G["📖 Adds citations\n(e.g. Page 625, Page 750)"]
    G --> H["🖥️ Chat UI\n(styled citation card + RAG badge)"]
    H --> A

    style A fill:#e0e7ff,stroke:#4f46e5,color:#1e1b4b
    style C fill:#eef2ff,stroke:#6366f1,color:#312e81
    style E fill:#f0fdf4,stroke:#22c55e,color:#166534
    style F fill:#fef3c7,stroke:#f59e0b,color:#78350f
    style H fill:#f1f5f9,stroke:#64748b,color:#1e293b
```

```mermaid
flowchart LR
    A["📂 GitHub Push"] --> B["🔨 Jenkins Pipeline"]
    B --> C["🐳 Docker Build"]
    C --> D["🔍 Trivy Security Scan"]
    D --> E["📦 GCP Artifact Registry"]
    E --> F["☁️ GCP Cloud Run"]
    F --> G["🌍 Live App"]

    style A fill:#f0fdf4,stroke:#22c55e,color:#166534
    style B fill:#e0e7ff,stroke:#4f46e5,color:#1e1b4b
    style D fill:#fef2f2,stroke:#ef4444,color:#991b1b
    style F fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style G fill:#fef3c7,stroke:#f59e0b,color:#78350f
```

## ✨ Features

- **RAG-Powered Answers** — Retrieves relevant context from a FAISS vector store built on a medical encyclopedia
- **Accurate Page Citations** — Uses PyMuPDF to extract real printed page numbers from the PDF (handles Roman numeral front matter and Arabic content pages), so citations match the physical book exactly
- **RAG Faithfulness** — Strict system prompt ensures the LLM only answers from retrieved context, never hallucinating from training knowledge. If the context doesn't cover the topic, it says so honestly
- **Modern LangChain Agent** — Uses the latest `create_agent` + `init_chat_model` API pattern
- **Conversational Memory** — Maintains chat history within a session using `InMemorySaver`
- **Clean UI** — Modern, responsive chat interface with styled citation cards and suggestion chips
- **CI/CD Pipeline** — Jenkins pipeline with Trivy security scanning and GCP Cloud Run deployment
- **Dockerized** — Production-ready Docker image using `uv` for fast dependency management

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Qwen3-32B via Groq API |
| **Agent Framework** | LangChain `create_agent` + LangGraph |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` |
| **Vector Store** | FAISS (local) |
| **PDF Processing** | PyMuPDF (fitz) — real page label extraction |
| **Backend** | Flask |
| **Frontend** | Pure HTML/CSS/JS |
| **Package Manager** | uv |
| **Containerization** | Docker |
| **CI/CD** | Jenkins (Docker-in-Docker) |
| **Cloud** | GCP (Artifact Registry + Cloud Run) |
| **Security Scan** | Trivy |

## 📁 Project Structure

```
medical-rag-ai-agent/
├── app/
│   ├── application.py              # Flask app entry point
│   ├── components/
│   │   ├── agent.py                # LangChain agent with RAG tool & citations
│   │   ├── embeddings.py           # HuggingFace embedding model setup
│   │   ├── vector_store.py         # FAISS vector store load/save
│   │   ├── pdf_loader.py           # PDF ingestion, real page label extraction (PyMuPDF) & text chunking
│   │   └── data_loader.py          # Pipeline: PDF → chunks → vector store
│   ├── common/
│   │   ├── logger.py               # Logging configuration
│   │   └── custom_exception.py     # Custom exception handler
│   ├── config/
│   │   └── config.py               # App configuration & env variables
│   └── templates/
│       └── index.html              # Chat UI template
├── data/
│   └── The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf
├── vectorstore/
│   └── db_faiss/                   # Pre-built FAISS index
├── custom_jenkins/
│   └── Dockerfile                  # Jenkins Docker-in-Docker image
├── Dockerfile                      # App Docker image (uv-based)
├── .dockerignore
├── Jenkinsfile                     # CI/CD pipeline (GCP)
├── pyproject.toml                  # Python dependencies
├── uv.lock                         # Locked dependencies
└── .python-version                 # Python 3.12
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- API keys for **Groq** and **HuggingFace**

### 1. Clone the Repository

```bash
git clone https://github.com/farhanrhine/medical-rag-ai-agent-gcp.git
cd medical-rag-ai-agent-gcp
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
GROQ_QWEN_MODEL=qwen/qwen3-32b
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Build the Vector Store (First Time Only)

If the `vectorstore/db_faiss/` directory is empty, generate it:

```bash
uv run python -m app.components.data_loader
```

### 5. Run the Application

```bash
uv run python -m app.application
```

Open **<http://127.0.0.1:5000>** in your browser.

## 🐳 Docker

### Build & Run Locally

```bash
docker build -t medical-rag-ai-agent .
docker run -p 5000:5000 --env-file .env medical-rag-ai-agent
```

## ☁️ GCP Deployment

The project is configured for deployment to **Google Cloud Platform** using:

- **Artifact Registry** — Docker image storage
- **Cloud Run** — Serverless container hosting

### CI/CD Pipeline (Jenkins)

The `Jenkinsfile` automates the full deployment:

```
Clone Repo → Build Image → Trivy Scan → Push to Artifact Registry → Deploy to Cloud Run
```

### Manual Deployment (gcloud CLI)

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build & push
docker build -t medical-rag-ai-agent .
docker tag medical-rag-ai-agent us-central1-docker.pkg.dev/YOUR_PROJECT_ID/medical-rag-ai-agent/medical-rag-ai-agent:latest
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/medical-rag-ai-agent/medical-rag-ai-agent:latest

# Deploy to Cloud Run
gcloud run deploy medical-rag-ai-agent \
    --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/medical-rag-ai-agent/medical-rag-ai-agent:latest \
    --region us-central1 \
    --port 5000 \
    --allow-unauthenticated
```

## 📖 How Citations Are Added

Most RAG systems cite "Page 15" — but that's just the PDF index, not the real book page. Our citations show the **actual printed page number** (e.g. Page 625) so you can verify it in the physical book.

**Step 1 — During Setup (one-time):**
- PyMuPDF opens each PDF page and reads the **footer text** at the bottom
- The footer has the real printed page number (e.g. "625") next to "GALE ENCYCLOPEDIA OF MEDICINE"
- This real number gets saved alongside each text chunk in the FAISS database
- So every chunk already knows: "I came from Page 625"

**Step 2 — When a User Asks a Question:**
- FAISS returns the top 3 matching chunks — each chunk comes **with its page number already attached**
- The LLM reads the chunks, sees `[Page 625]`, `[Page 627]`, etc.
- The LLM writes a short answer and appends: `📖 Sources: Page 625, Page 627`
- It only cites pages that **directly answered** the question (not every retrieved page)

**Step 3 — In the UI:**
- JavaScript finds the `📖 Sources:` text in the response
- Converts it into a styled green citation card with a `✅ RAG-Verified Answer` badge

This means when the app says "Page 750", you can flip to page 750 in the book and verify the answer word-for-word.

## 🏗️ Architecture

See the [Workflow diagrams](#-workflow) at the top of this README for the full application and CI/CD flow.


## 👤 Author

**Farhan** — [GitHub](https://github.com/farhanrhine)
