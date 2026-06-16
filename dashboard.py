import streamlit as st
import pandas as pd
import plotly.express as px
from database import SessionLocal, AttendanceHistory
from attendance_calculator import calculate_subject_wise, calculate_overall, get_attendance_status

def fetch_user_attendance(student_id):
    """Fetches attendance history from the database and returns a DataFrame."""
    db = SessionLocal()
    records = db.query(AttendanceHistory).filter(AttendanceHistory.student_id == student_id).all()
    db.close()
    
    if not records:
        return pd.DataFrame()
        
    data = [{"Subject": r.subject, "Present": r.classes_present, "Total": r.total_classes} for r in records]
    return pd.DataFrame(data)

def render():
    student_id = st.session_state['user_data']['student_id']
    df = fetch_user_attendance(student_id)

    if df.empty:
        st.info("No attendance data found. Please go to 'Update Attendance' to add your records.")
        return

    # --- Calculations ---
    df = calculate_subject_wise(df)
    overall_pct = calculate_overall(df)
    status, delta_color = get_attendance_status(overall_pct)

    # --- Top Metrics Cards ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Overall Attendance", value=f"{overall_pct}%", delta=status, delta_color=delta_color)
    with col2:
        total_classes = int(df['Total'].sum())
        st.metric(label="Total Classes Held", value=total_classes)
    with col3:
        total_present = int(df['Present'].sum())
        st.metric(label="Total Attended", value=total_present)
    with col4:
        classes_missed = total_classes - total_present
        st.metric(label="Classes Missed", value=classes_missed)

    st.divider()

    # --- Charts & Detailed Tables ---
    col_chart, col_table = st.columns([1.5, 1])

    with col_chart:
        st.markdown("### Subject-Wise Analysis")
        # Plotly Bar Chart
        fig = px.bar(
            df, 
            x='Subject', 
            y='Percentage', 
            color='Percentage',
            color_continuous_scale=["#FF4B4B", "#FFA500", "#00C853"], # Red -> Orange -> Green
            range_color=[50, 100],
            range_y=[0, 100],
            text='Percentage'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20)
        )
        # Add 75% criteria line
        fig.add_hline(y=75, line_dash="dash", line_color="#FF4B4B", annotation_text="75% Minimum")
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("### Breakdown")
        # Display styled dataframe
        st.dataframe(
            df[['Subject', 'Present', 'Total', 'Percentage']],
            hide_index=True,
            use_container_width=True
        )

    # --- Quick AI Status Check ---
    st.divider()
    st.markdown("### 🤖 Quick Status Check")
    if overall_pct >= 75:
        st.success("Great job! You are maintaining a healthy attendance record above the 75% requirement.")
    else:
        st.error("Your overall attendance is below 75%. Check the 'Safe Holiday Calculator' and 'Future Predictor' to plan your recovery.")