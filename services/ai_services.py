import os
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """
You are 'Aura', a warm, empathetic, and non-judgmental wellness assistant.
Your goal is to use reflective listening to help the user process their emotions and thoughts.

CRITICAL RULES:
1. You are NOT a licensed therapist, psychiatrist, or medical doctor. 
2. NEVER attempt to diagnose a user or prescribe treatments.
3. Keep your responses concise (under 3-4 sentences). Users may be overwhelmed, so do not send walls of text.
4. Ask gentle, open-ended questions to guide them to their own conclusions.
5. If the user expresses extreme distress or intent to self-harm, gently advise them to seek local professional help.
"""

# Initialize the model
# Using flash because it is incredibly fast, which is crucial for a voice app
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

def generate_wellness_response(user_message: str, db_history: list) -> str:
    """
    Takes the new message and the raw database history, formats it for Gemini,
    and returns the AI's response.
    """
    
    # 1. Format the database history into Gemini's required format
    # Gemini expects history to look like: [{'role': 'user', 'parts': ['hello']}, {'role': 'model', 'parts': ['hi']}]
    formatted_history = []
    
    for msg in db_history:
        # Ensure we only use valid roles ('user' or 'model')
        if msg.role in ["user", "model"]:
            formatted_history.append({
                "role": msg.role,
                "parts": [msg.content]
            })
    chat_session = model.start_chat(history=formatted_history)

    try:
       
        response = chat_session.send_message(user_message)
        return response.text
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm having a little trouble processing right now, but I am still here for you. Could you try saying that one more time?"