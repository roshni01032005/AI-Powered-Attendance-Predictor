import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from dotenv import load_dotenv
from database import SessionLocal, AttendanceHistory

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    # Using Gemini 1.5 Flash for fast text generation
    model = genai.GenerativeModel('gemini-2.5-flash') 
else:
    st.error("⚠️ GEMINI_API_KEY not found in .env file.")

def fetch_attendance(student_id):
    db = SessionLocal()
    records = db.query(AttendanceHistory).filter(AttendanceHistory.student_id == student_id).all()
    db.close()
    if not records:
        return pd.DataFrame()
    return pd.DataFrame([{"Subject": r.subject, "Present": r.classes_present, "Total": r.total_classes} for r in records])

def render():
    st.write("Get personalized AI recommendations for your attendance and career.")
    
    tab1, tab2 = st.tabs(["📊 Attendance Advisor", "🎯 Career Guidance"])
    
    student_id = st.session_state['user_data']['student_id']
    branch = st.session_state['user_data']['branch']
    semester = st.session_state['user_data']['semester']

    with tab1:
        st.subheader("Smart Attendance Recovery Plans")
        df = fetch_attendance(student_id)
        
        if df.empty:
            st.info("Please update your attendance in the 'Update Attendance' tab first.")
        else:
            if st.button("Generate Attendance Strategy"):
                with st.spinner("Analyzing your attendance data..."):
                    try:
                        # Convert dataframe to a string for the AI to read
                        data_str = df.to_string(index=False)
                        prompt = f"""
                        You are an academic advisor. A student in {branch}, Semester {semester} has the following attendance:
                        {data_str}
                        
                        The target attendance is 75%. 
                        1. Provide a brief analysis of their current standing.
                        2. Give specific, actionable subject-wise recommendations (e.g., "Attend next 4 OS classes continuously").
                        3. Provide a brief motivational closing.
                        Keep it concise, encouraging, and easy to read.
                        """
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"AI Error: {str(e)}")

    with tab2:
        st.subheader("AI Career & Skill Recommendations")
        st.write(f"Tailored for: **{branch} | Semester {semester}**")
        
        user_query = st.text_input("Ask a career question:", placeholder="E.g., What field suits me if I like Python and logic?")
        
        if st.button("Ask Career AI"):
            if user_query:
                with st.spinner("Consulting industry trends..."):
                    try:
                        prompt = f"""
                        You are an expert career counselor for engineering/college students.
                        The student is in {branch}, Semester {semester}.
                        They asked: "{user_query}"
                        
                        Provide:
                        1. 2-3 Career Suggestions
                        2. 3-4 Specific Skill Recommendations to learn right now
                        3. Quick placement/internship guidance
                        Keep the tone professional, highly structured with bullet points, and realistic.
                        """
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"AI Error: {str(e)}")
            else:
                st.warning("Please enter a question first.")