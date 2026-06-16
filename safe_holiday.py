import streamlit as st
import pandas as pd
from database import SessionLocal, AttendanceHistory
import math

def fetch_attendance(student_id):
    db = SessionLocal()
    records = db.query(AttendanceHistory).filter(AttendanceHistory.student_id == student_id).all()
    db.close()
    if not records:
        return pd.DataFrame()
    return pd.DataFrame([{"Subject": r.subject, "Present": r.classes_present, "Total": r.total_classes} for r in records])

def calculate_safe_holidays(present, total, target_percentage=75):
    """
    Calculates how many classes can be missed to maintain target percentage.
    Formula: (Present / Target) - Total
    """
    if total == 0:
        return 0, 0
    
    current_percentage = (present / total) * 100
    target_decimal = target_percentage / 100.0

    if current_percentage >= target_percentage:
        # Calculate classes we can miss
        safe_to_miss = math.floor((present / target_decimal) - total)
        return "Safe", safe_to_miss
    else:
        # Calculate classes we need to attend continuously
        # (Present + required) / (Total + required) = target_decimal
        # required = (target_decimal * Total - Present) / (1 - target_decimal)
        required_to_attend = math.ceil((target_decimal * total - present) / (1 - target_decimal))
        return "Critical", required_to_attend

def render():
    student_id = st.session_state['user_data']['student_id']
    df = fetch_attendance(student_id)

    if df.empty:
        st.warning("Please update your attendance first to calculate safe holidays.")
        return

    st.write("Find out how many classes you can comfortably miss, or how many you need to attend to recover your attendance.")
    
    target = st.slider("Target Attendance %", min_value=60, max_value=90, value=75, step=5)
    st.divider()

    col1, col2 = st.columns(2)
    
    for index, row in df.iterrows():
        subject = row['Subject']
        present = row['Present']
        total = row['Total']
        status, count = calculate_safe_holidays(present, total, target)
        
        # Alternate between columns for better UI layout
        col = col1 if index % 2 == 0 else col2
        
        with col:
            with st.container(border=True):
                st.subheader(subject)
                current_pct = round((present/total)*100, 2) if total > 0 else 0
                st.write(f"Current: **{current_pct}%** ({present}/{total})")
                
                if status == "Safe":
                    st.success(f"🎉 Safe to miss: **{count} classes**")
                else:
                    st.error(f"🚨 Must attend: **{count} consecutive classes**")