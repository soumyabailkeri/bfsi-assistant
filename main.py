from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from database import SessionLocal, ConversationLog
import os
import uuid

load_dotenv()

app = FastAPI(title="BFSI Assistant API")

# LLM — no tools bound, we handle everything in the prompt
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """You are a helpful BFSI (Banking, Financial Services and Insurance) assistant at an Indian bank.
You help customers with banking queries, loan assessments, and financial advice.

You have deep knowledge about:
- Credit scores (300-900 range in India, 750+ is excellent)
- Loan types: Home Loans (8-9%), Personal Loans (10-24%), Car Loans (7-9%), Education Loans (8-15%), Business Loans (10-18%)
- KYC requirements: Aadhaar, PAN, address proof, income proof
- Fixed Deposits: 5-7.5% interest, senior citizens get extra 0.25-0.5%
- International remittances via SWIFT, NEFT, RTGS
- Teller operations, cash management, paper remittance processing
- Loan eligibility factors: credit score, income, employment stability, debt-to-income ratio

For loan risk assessment, consider:
- Age 18-60 preferred
- Stable employment (2+ years preferred)  
- Income to loan ratio (loan should be less than 5x annual income)
- Good credit score (700+)

Always be professional, accurate, and helpful. Give specific numbers and advice when possible."""

# Session memory store
session_histories = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
def home():
    return {"message": "BFSI Assistant API is running"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Create or get session
    session_id = request.session_id or str(uuid.uuid4())

    # Get or create history
    if session_id not in session_histories:
        session_histories[session_id] = []

    history = session_histories[session_id]

    # Build messages
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add conversation history
    for h in history:
        messages.append(HumanMessage(content=h["user"]))
        messages.append(AIMessage(content=h["assistant"]))

    # Add current message
    messages.append(HumanMessage(content=request.message))

    # Call LLM
    response = llm.invoke(messages)
    ai_response = response.content

    # Update memory
    session_histories[session_id].append({
        "user": request.message,
        "assistant": ai_response
    })

    # Log to database
    log = ConversationLog(
        session_id=session_id,
        user_message=request.message,
        ai_response=ai_response
    )
    db.add(log)
    db.commit()

    return {"response": ai_response, "session_id": session_id}

@app.get("/conversations/{session_id}")
def get_conversation(session_id: str, db: Session = Depends(get_db)):
    logs = db.query(ConversationLog).filter(
        ConversationLog.session_id == session_id
    ).order_by(ConversationLog.created_at).all()
    return [
        {
            "user": log.user_message,
            "assistant": log.ai_response,
            "time": log.created_at
        }
        for log in logs
    ]

@app.get("/conversations")
def get_all_conversations(db: Session = Depends(get_db)):
    logs = db.query(ConversationLog).order_by(
        ConversationLog.created_at.desc()
    ).limit(20).all()
    return [
        {
            "session_id": log.session_id,
            "user": log.user_message,
            "assistant": log.ai_response,
            "time": log.created_at
        }
        for log in logs
    ]

@app.get("/health")
def health():
    return {"status": "ok"}