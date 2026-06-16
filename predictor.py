import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import SessionLocal, AttendanceHistory

def fetch_attendance(student_id):
    db = SessionLocal()
    records = db.query(AttendanceHistory).filter(AttendanceHistory.student_id == student_id).all()
    db.close()
    if not records:
        return pd.DataFrame()
    return pd.DataFrame([{"Subject": r.subject, "Present": r.classes_present, "Total": r.total_classes} for r in records])

def generate_prediction_data(present, total):
    """Generates future attendance scenarios based on rules."""
    scenarios = [5, 10, 20]
    best_case = []
    worst_case = []
    
    for classes in scenarios:
        # Best case: Attend all upcoming classes
        best_pct = ((present + classes) / (total + classes)) * 100
        best_case.append(round(best_pct, 2))
        
        # Worst case: Miss all upcoming classes
        worst_pct = (present / (total + classes)) * 100
        worst_case.append(round(worst_pct, 2))
        
    return scenarios, best_case, worst_case

def render():
    student_id = st.session_state['user_data']['student_id']
    df = fetch_attendance(student_id)

    if df.empty:
        st.warning("Please add attendance data to see predictions.")
        return

    st.write("Rule-based prediction of your attendance trajectory if you attend (or miss) the next few classes.")
    
    selected_subject = st.selectbox("Select Subject to Analyze", df['Subject'].tolist())
    
    subject_data = df[df['Subject'] == selected_subject].iloc[0]
    present = subject_data['Present']
    total = subject_data['Total']
    
    current_pct = round((present/total)*100, 2) if total > 0 else 0
    
    scenarios, best_case, worst_case = generate_prediction_data(present, total)
    
    # Plotly Line Chart
    fig = go.Figure()
    
    # Add Current point (0 classes ahead)
    x_axis = [0] + scenarios
    best_line = [current_pct] + best_case
    worst_line = [current_pct] + worst_case
    
    fig.add_trace(go.Scatter(x=x_axis, y=best_line, mode='lines+markers+text', 
                             name='Best Case (Attend All)', line=dict(color='#00C853', width=3),
                             text=[f"{v}%" for v in best_line], textposition="top center"))
                             
    fig.add_trace(go.Scatter(x=x_axis, y=worst_line, mode='lines+markers+text', 
                             name='Worst Case (Miss All)', line=dict(color='#FF4B4B', width=3),
                             text=[f"{v}%" for v in worst_line], textposition="bottom center"))

    fig.add_hline(y=75, line_dash="dash", line_color="gray", annotation_text="75% Threshold")

    fig.update_layout(
        title=f"Attendance Trajectory for {selected_subject}",
        xaxis_title="Upcoming Classes",
        yaxis_title="Predicted Attendance %",
        yaxis=dict(range=[0, 100]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)