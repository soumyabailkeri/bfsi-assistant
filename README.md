# BFSI Assistant API

An AI-powered conversational assistant for Banking, Financial Services and Insurance — built with LangChain, Groq LLMs, RAG, FastAPI, and PostgreSQL. Combines large language model capabilities with real banking domain expertise and document-grounded responses.

---

## What it does

Two core capabilities in one API:

**1. Conversational Banking Assistant** — Multi-turn conversations with memory. Ask follow-up questions naturally, get professional banking advice.

**2. RAG Policy Engine** — Ask questions about banking policy documents and get accurate, cited answers grounded in the actual document — not LLM guesswork.

---

## Example — Conversational Chat

**Request:**
```json
{
    "message": "What credit score do I need for a home loan?",
    "session_id": null
}
```

**Response:**
```json
{
    "response": "For a home loan in India, you generally need a minimum credit score of 700. A score of 750 or above is considered excellent and will help you secure better interest rates, typically around 8-8.5%. Scores below 650 may result in rejection or significantly higher rates.",
    "session_id": "f5b229fe-f2f5-4f0b-9e54-9d125d86e1ec"
}
```

**Follow-up using same session_id:**
```json
{
    "message": "What was my previous question?",
    "session_id": "f5b229fe-f2f5-4f0b-9e54-9d125d86e1ec"
}
```
The AI remembers — full session memory working.

---

## Example — RAG Policy Query

**Request:**
```json
{
    "question": "What is the maximum cash withdrawal at a branch per day?"
}
```

**Response:**
```json
{
    "question": "What is the maximum cash withdrawal at a branch per day?",
    "answer": "The maximum cash withdrawal per day at a branch is Rs 1,00,000 (Section: CASH WITHDRAWAL POLICY).",
    "source": "banking_policy.txt"
}
```

Answers cite the exact policy section — no hallucination.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| LLM | Groq (LLaMA 3.3 70B) via LangChain |
| RAG | ChromaDB + HuggingFace Embeddings |
| Memory | Session-based conversation history |
| Database | PostgreSQL (conversation logging) |
| ORM | SQLAlchemy |
| Containerisation | Docker + docker-compose |
| Documentation | Auto-generated Swagger UI |

---

## Architecture

```
Conversational Flow:
POST /chat
    → Session ID created or retrieved
    → Conversation history loaded
    → System prompt + history + message sent to LLM
    → Response appended to session memory
    → Conversation logged to PostgreSQL
    → Response returned with session_id

RAG Flow:
POST /policy/ask
    → Question converted to embedding vector
    → ChromaDB searches for similar policy chunks
    → Top 3 relevant chunks retrieved
    → LLM answers using chunks as context
    → Answer returned with source citation
```

---

## Running Locally

### Option 1 — Docker (recommended)
```bash
git clone https://github.com/soumyabailkeri/bfsi-assistant.git
cd bfsi-assistant
cp .env.example .env
# Add your GROQ_API_KEY to .env
docker compose up --build
```

### Option 2 — Without Docker
```bash
git clone https://github.com/soumyabailkeri/bfsi-assistant.git
cd bfsi-assistant
pip install -r requirements.txt
# Add GROQ_API_KEY to .env file
uvicorn main:app --reload --port 8002
```

Get a free Groq API key at console.groq.com

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/health` | Service status |
| POST | `/chat` | Multi-turn conversation with memory |
| GET | `/conversations` | All conversation history |
| GET | `/conversations/{session_id}` | Specific session history |
| POST | `/policy/ask` | RAG-based policy document query |
| GET | `/docs` | Interactive Swagger documentation |

---

## Key Features

**Session Memory**
Each conversation gets a unique `session_id`. Send it back with follow-up messages and the AI remembers the full context of your conversation.

**RAG — Document Grounded Answers**
Banking policy questions are answered using actual document content, not LLM training data. Responses cite the exact policy section — critical for compliance use cases.

**PostgreSQL Logging**
Every conversation is logged with session ID and timestamp — full audit trail for compliance and analytics.

**BFSI Domain Expertise**
System prompt engineered with real banking knowledge: credit score ranges, loan types with Indian interest rates, KYC requirements, remittance regulations, teller operations — drawn from 3 years of professional BFSI experience.

---

## Project Structure

```
bfsi-assistant/
├── main.py                 # FastAPI app, chat endpoint, memory
├── rag.py                  # RAG pipeline, ChromaDB, embeddings
├── database.py             # SQLAlchemy models, conversation logs
├── banking_policy.txt      # Sample banking policy document
├── chroma_db/              # Persisted vector store
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build instructions
├── docker-compose.yml      # Multi-container orchestration
└── .gitignore              # Excludes .env and secrets
```

---

## JD Alignment

This project was built specifically to demonstrate skills relevant to Senior Python + GenAI engineering roles:

| JD Requirement | Implementation |
|---|---|
| LLM integration | Groq LLaMA 3.3 70B via LangChain |
| Memory/context management | Session-based conversation history |
| RAG pipelines | ChromaDB + HuggingFace embeddings |
| Vector database | ChromaDB with similarity search |
| FastAPI + REST APIs | Full API with Swagger docs |
| PostgreSQL | Conversation audit logging |
| Docker | Containerised multi-service deployment |
| BFSI domain | Banking assistant with domain knowledge |

---

## Author

**Soumya Bailkeri**
Backend Software Engineer | Python · FastAPI · LangChain · BFSI
[LinkedIn](https://linkedin.com/in/soumyabailkeri) · [GitHub](https://github.com/soumyabailkeri)