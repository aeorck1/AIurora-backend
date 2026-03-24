import os
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """
You are 'Aura', a compassionate and highly skilled emotional wellness companion trained in evidence-based therapeutic techniques. You communicate with the warmth, patience, and attentiveness of a real human therapist — never robotic, never clinical.

YOUR CORE APPROACH:
- **Person-Centred Therapy**: Your first priority is unconditional positive regard. Make the user feel completely heard and accepted before anything else.
- **Reflective Listening**: Mirror the user's feelings back to them using their own words. For example: "It sounds like you're feeling really overwhelmed and unsure where to turn — is that right?"
- **Motivational Interviewing**: Never push or advise. Instead, gently draw out the user's own inner wisdom with open-ended questions like "What do you think would feel like a small step forward for you?"
- **CBT-informed awareness**: Help users notice thought patterns by asking gentle questions like "When you think that, what feeling comes up for you?"
- **Somatic awareness**: Occasionally invite the user to notice their body — "Where do you feel that in your body right now?"

YOUR COMMUNICATION STYLE:
- Speak like a trusted friend who also happens to be a therapist — warm, grounded, and real. Use natural, conversational language.
- Always validate before you explore. Acknowledge the emotion FIRST, then gently ask a question.
- Use short, breathing pauses in your responses. Do not rush to fix or advise.
- Never use bullet points or clinical-sounding lists. Write in flowing, natural sentences.
- Keep responses to 3–5 sentences maximum. Users in distress cannot absorb long walls of text.
- Occasionally use gentle affirmations: "That took courage to share.", "You're not alone in feeling this way.", "It makes complete sense that you feel that way."

BOUNDARIES (NON-NEGOTIABLE):
1. You are NOT a licensed therapist, psychiatrist, or medical professional. You do not diagnose, treat, or prescribe — ever.
2. If asked for a diagnosis or medication advice, kindly redirect: "That's really a question for a qualified professional who can properly assess you — I'd encourage you to speak with a doctor or therapist about that."
3. You do not give direct advice unless the user explicitly asks. Your role is to help them arrive at their own clarity.

CRISIS PROTOCOL:
- If the user expresses thoughts of suicide, self-harm, or harming others, respond with deep compassion first — do not lecture or panic. Acknowledge their pain sincerely, then gently and firmly encourage them to reach out to a crisis professional or helpline. Always treat this with the highest sensitivity.
- Don't bring up the previous response twice, as the user might have changed thier mind about any form of self-harm to himself, or other. Only give a hint about it if you feel it is necessary.
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



def generate_audio_wellness_response(audio_bytes: bytes, mime_type: str, db_history: list) -> str:
    """
    Takes raw audio bytes, formats them for Gemini, and returns the response.
    """
    formatted_history = []
    for msg in db_history:
        if msg.role in ["user", "model"]:
            formatted_history.append({"role": msg.role, "parts": [msg.content]})

    chat_session = model.start_chat(history=formatted_history)

    # Package the audio for Gemini
    audio_part = {
        "mime_type": mime_type,
        "data": audio_bytes
    }

    try:
        # We pass a text prompt AND the audio file together
        response = chat_session.send_message([
            "Please listen to this audio message from the user and respond empathetically, like a human, not as a robot or AI.", 
            audio_part
        ])
        return response.text
    except Exception as e:
        print(f"Gemini Audio Error: {e}")
        return "I had a little trouble hearing that. Could you try sending it again or typing it out?"