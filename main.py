import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


# Import DB and Schemas
from models.database import get_db, User, Message
from models.schemas import ChatRequest, ChatResponse, MessageHistory
from services.ai_services import generate_wellness_response
from api.routes import router

# Load environment variables
load_dotenv()

app = FastAPI(title="Aura Wellness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")
