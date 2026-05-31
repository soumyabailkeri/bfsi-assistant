from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from database import SessionLocal, ConversationLog
from tools import assess_loan_risk, get_banking_info
import os
import uuid

load_dotenv()

app = FastAPI(title="BFSI Assistant API")

# LLM with tools bound directly
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

llm_with_tools = llm.bind_tools([assess_loan_risk, get_banking_info])

# System prompt
SYSTEM_PROMPT = """You are a helpful BFSI (Banking, Financial Services and Insurance) assistant.
You help customers with banking queries, loan assessments, and financial advice.
You have access to tools to assess loan risk and provide banking information.
Always be professional, accurate, and helpful.
If asked about loan eligibility, use the assess_loan_risk tool.
If asked about banking concepts, use the get_banking_info tool."""

# Session memory store — stores conversation history per session
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

    # Get or create history for this session
    if session_id not in session_histories:
        session_histories[session_id] = []

    history = session_histories[session_id]

    # Build messages list
    messages = [("system", SYSTEM_PROMPT)]
    for h in history:
        messages.append(("human", h["user"]))
        messages.append(("assistant", h["assistant"]))
    messages.append(("human", request.message))

    # Call LLM
    response = llm_with_tools.invoke(messages)
    ai_response = response.content

    # If LLM wants to use a tool
    if response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            if tool_name == "assess_loan_risk":
                result = assess_loan_risk.invoke(tool_args)
            elif tool_name == "get_banking_info":
                result = get_banking_info.invoke(tool_args)
            else:
                result = "Tool not found"
            tool_results.append(result)

        # Send tool results back to LLM for final response
        messages.append(("assistant", str(response.tool_calls)))
        messages.append(("human", f"Tool results: {', '.join(tool_results)}. Now give the user a helpful response based on these results."))
        final_response = llm_with_tools.invoke(messages)
        ai_response = final_response.content

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