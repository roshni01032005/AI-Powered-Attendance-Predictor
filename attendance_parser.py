import streamlit as st
import pandas as pd
import re
from database import SessionLocal, AttendanceHistory

def parse_attendance_text(raw_text):
    """
    Parses raw text pasted from a college portal.
    Extracts Subject, Present, and Total using regex.
    """
    try:
        # Split into lines and remove empty ones
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        if not lines:
            return None, "No data found. Please paste the text."

        data = []
        for line in lines:
            # Matches text (Subject), followed by spaces, a number (Present), spaces, a number (Total)
            match = re.search(r'^(.*?)\s+(\d+)\s+(\d+)$', line)
            if match:
                subject = match.group(1).strip()
                present = int(match.group(2))
                total = int(match.group(3))
                
                # Ignore table headers if they accidentally contain numbers (rare but possible)
                if subject.lower() != "subject": 
                    data.append({"Subject": subject, "Present": present, "Total": total})

        if not data:
            return None, "Could not extract valid data. Please ensure it matches the example format."

        df = pd.DataFrame(data)
        return df, "Success"
    except Exception as e:
        return None, f"Parsing error: {str(e)}"

def save_to_database(df, student_id):
    """Saves parsed DataFrame to the SQLite Database."""
    db = SessionLocal()
    try:
        for _, row in df.iterrows():
            # Check if record exists to update it, or create a new one
            existing_record = db.query(AttendanceHistory).filter(
                AttendanceHistory.student_id == student_id,
                AttendanceHistory.subject == row['Subject']
            ).first()

            if existing_record:
                existing_record.classes_present = row['Present']
                existing_record.total_classes = row['Total']
            else:
                new_record = AttendanceHistory(
                    student_id=student_id,
                    subject=row['Subject'],
                    classes_present=row['Present'],
                    total_classes=row['Total']
                )
                db.add(new_record)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        st.error(f"Database error: {e}")
        return False
    finally:
        db.close()

def render():
    """Renders the Streamlit UI for this module."""
    st.write("Paste your attendance data directly from your college ERP/Portal.")
    
    with st.expander("📝 View Example Format"):
        st.code("""Subject     Present     Total
DAA         35          40
OS          30          42
DBMS        32          38""", language='text')

    raw_text = st.text_area("Paste Data Here:", height=200, placeholder="E.g.\nMaths 15 20\nPhysics 18 22")
    
    if st.button("Parse and Save Attendance", type="primary"):
        if raw_text:
            df, message = parse_attendance_text(raw_text)
            if df is not None:
                st.success("Data parsed successfully!")
                st.dataframe(df, use_container_width=True)
                
                # Save to database using session state user ID
                student_id = st.session_state['user_data']['student_id']
                if save_to_database(df, student_id):
                    st.success("Attendance successfully synced to the database!")
            else:
                st.error(message)
        else:
            st.warning("Please paste some data first.")