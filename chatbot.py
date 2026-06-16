import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from database import SessionLocal, ChatHistory

# Load API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    
    # System prompt applying the required guardrails
    system_instruction = """
    You are EduAssist, a supportive student mentor and wellness assistant.
    You help students with: Stress, Anxiety, Exam Pressure, Career Confusion, and Motivation.
    CRITICAL RULES:
    1. You are NOT a doctor or licensed therapist. Never claim to be one.
    2. If a student mentions severe mental health risks, self-harm, or extreme distress, you MUST immediately and gently recommend they seek professional medical help or contact a local emergency helpline.
    3. Keep responses empathetic, concise, and structured. 
    """
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=system_instruction
    )
else:
    st.error("⚠️ GEMINI_API_KEY not found in .env file.")

def load_chat_history(student_id):
    """Loads chat history from the SQLite database."""
    db = SessionLocal()
    history = db.query(ChatHistory).filter(ChatHistory.student_id == student_id).order_by(ChatHistory.timestamp).all()
    db.close()
    return [{"role": h.role, "content": h.content} for h in history]

def save_chat_message(student_id, role, content):
    """Saves a single message to the SQLite database."""
    db = SessionLocal()
    try:
        new_msg = ChatHistory(student_id=student_id, role=role, content=content)
        db.add(new_msg)
        db.commit()
    except Exception as e:
        st.error(f"Failed to save chat: {e}")
    finally:
        db.close()

def render():
    st.write("Talk to your AI mentor about stress, exams, or anything on your mind.")
    student_id = st.session_state['user_data']['student_id']

    # Initialize session state for UI rendering if empty
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history(student_id)

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("How are you feeling today?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        
        # Add user message to session state and database
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_chat_message(student_id, "user", prompt)

        # Generate AI response
        with st.chat_message("model"):
            message_placeholder = st.empty()
            
            # Format history for Gemini API
            gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            
            try:
                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(prompt)
                
                # Display and save response
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
                save_chat_message(student_id, "model", response.text)
                
            except Exception as e:
                st.error(f"Connection error: {str(e)}")