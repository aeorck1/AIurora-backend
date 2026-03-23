import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import our DB and Schemas
from models.database import get_db, User, Message
from models.schemas import ChatRequest, ChatResponse, MessageHistory
from services.ai_services import generate_wellness_response

# Load environment variables (like your Gemini API key)
load_dotenv()

app = FastAPI(title="Aura Wellness API")

# Allow React Native to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINTS ---

@app.post("/api/users")
def create_user(db: Session = Depends(get_db)):
    """Creates an anonymous user session."""
    new_user = User()
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user_id": new_user.id}

@app.get("/api/chat/{user_id}", response_model=list[MessageHistory])
def get_chat_history(user_id: str, db: Session = Depends(get_db)):
    """Fetches history so the mobile app can display past messages."""
    messages = db.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at).all()
    return messages

@app.post("/api/chat", response_model=ChatResponse)
def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Handles the core chat logic."""
    
    # 1. Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Save user's incoming message to DB
    user_msg = Message(user_id=request.user_id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    # 3. Local Crisis Filter (MANI routing for Nigeria)
    crisis_keywords = ["suicide", "kill", "kill myself", "killing myself", "end it all", "harm myself"]
    if any(word in request.message.lower() for word in crisis_keywords):
        crisis_reply = "This sounds incredibly difficult. Please know you are not alone. In Nigeria, you can reach the Mentally Aware Nigeria Initiative (MANI) at 08091116264 or 08111680686. Please reach out to them."
        
        ai_msg = Message(user_id=request.user_id, role="model", content=crisis_reply)
        db.add(ai_msg)
        db.commit()
        return ChatResponse(reply=crisis_reply, is_crisis=True)

    # --- THE NEW AI INTEGRATION ---
    
    # 4. Fetch the user's chat history from the database (excluding the message we just saved)
    # We limit it to the last 20 messages to save on API tokens and keep context relevant
    chat_history = db.query(Message).filter(
        Message.user_id == request.user_id, 
        Message.id != user_msg.id
    ).order_by(Message.created_at.desc()).limit(20).all()
    
    # Reverse it so it's in chronological order for the AI
    chat_history.reverse()

    # 5. Call our new AI service!
    ai_reply = generate_wellness_response(request.message, chat_history)
    
    # -----------------------------
    ai_msg = Message(user_id=request.user_id, role="model", content=ai_reply)
    db.add(ai_msg)
    db.commit()

    return ChatResponse(reply=ai_reply, is_crisis=False)