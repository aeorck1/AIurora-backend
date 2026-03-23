from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import our database, schemas, and security
from models.database import get_db, User, Message
from models.schemas import ChatRequest, ChatResponse, MessageHistory
from core.security import validate_uuid
from core.config import settings

# Import our AI Brain
from services.ai_service import generate_wellness_response

# Create the router (this acts like a mini-FastAPI app)
router = APIRouter()

@router.post("/users")
def create_user(db: Session = Depends(get_db)):
    """Creates a new anonymous user session."""
    new_user = User()
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user_id": new_user.id}

@router.get("/chat/{user_id}", response_model=list[MessageHistory])
def get_chat_history(user_id: str, db: Session = Depends(get_db)):
    """Fetches history so the mobile app can display past messages."""
    # 1. Run the user_id through our security bouncer!
    safe_user_id = validate_uuid(user_id)
    
    messages = db.query(Message).filter(Message.user_id == safe_user_id).order_by(Message.created_at).all()
    return messages

@router.post("/chat", response_model=ChatResponse)
def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Handles the core chat logic."""
    # 1. Run the incoming ID through the security bouncer
    safe_user_id = validate_uuid(request.user_id)
    
    # 2. Verify user exists in the database
    user = db.query(User).filter(User.id == safe_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Save user's incoming message to DB
    user_msg = Message(user_id=safe_user_id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    # 4. Local Crisis Filter (Using the MANI hotline from our config file!)
    crisis_keywords = ["suicide", "kill myself", "end it all", "harm myself"]
    if any(word in request.message.lower() for word in crisis_keywords):
        crisis_reply = f"This sounds incredibly difficult. Please know you are not alone. In Nigeria, you can reach the Mentally Aware Nigeria Initiative (MANI) at {settings.CRISIS_HOTLINE_NG}. Please reach out to them."
        
        ai_msg = Message(user_id=safe_user_id, role="model", content=crisis_reply)
        db.add(ai_msg)
        db.commit()
        return ChatResponse(reply=crisis_reply, is_crisis=True)

    # 5. Fetch the user's chat history (last 20 messages for context)
    chat_history = db.query(Message).filter(
        Message.user_id == safe_user_id, 
        Message.id != user_msg.id
    ).order_by(Message.created_at.desc()).limit(20).all()
    
    chat_history.reverse()

    # 6. Call the Gemini AI service
    ai_reply = generate_wellness_response(request.message, chat_history)
    
    # 7. Save AI's response to DB
    ai_msg = Message(user_id=safe_user_id, role="model", content=ai_reply)
    db.add(ai_msg)
    db.commit()

    return ChatResponse(reply=ai_reply, is_crisis=False)