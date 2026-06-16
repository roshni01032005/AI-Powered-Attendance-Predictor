import streamlit as st
from database import init_db, SessionLocal
from auth import authenticate_user, register_user
from utils import get_greeting

# Must be the first Streamlit command
st.set_page_config(
    page_title="EduAssist AI | Student Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# --- Custom CSS for Modern UI ---
def load_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #4A90E2;
            margin-bottom: 1rem;
        }
        .card {
            background-color: #1E2127;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            margin-bottom: 1rem;
        }
        div[data-testid="stSidebar"] {
            background-color: #161B22;
            border-right: 1px solid #30363D;
        }
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

# --- UI Components ---
def login_page():
    st.markdown('<div class="main-header">Welcome to EduAssist AI</div>', unsafe_allow_html=True)
    st.write("Your AI-Powered Attendance Predictor and Wellness Assistant")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Login")
            student_id = st.text_input("Student ID")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                if not student_id or not password:
                    st.error("Please fill in all fields.")
                else:
                    db = SessionLocal()
                    success, result = authenticate_user(db, student_id, password)
                    db.close()
                    
                    if success:
                        st.session_state['logged_in'] = True
                        st.session_state['user_data'] = {
                            "student_id": result.student_id,
                            "name": result.name,
                            "branch": result.branch,
                            "semester": result.semester
                        }
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result)

def register_page():
    st.markdown('<div class="main-header">Create an Account</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("register_form"):
            st.subheader("Register")
            student_id = st.text_input("Student ID")
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            branch = st.selectbox("Branch", ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil"])
            semester = st.number_input("Semester", min_value=1, max_value=8, value=1)
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if not all([student_id, name, email, password, confirm_password]):
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    db = SessionLocal()
                    success, message = register_user(db, student_id, name, email, password, branch, semester)
                    db.close()
                    
                    if success:
                        st.success(message + " Please proceed to login.")
                    else:
                        st.error(message)

def main_app():
    # Sidebar Navigation
    with st.sidebar:
        greeting = get_greeting()
        st.write(f"### 👋 {greeting}, {st.session_state['user_data']['name']}")
        st.write(f"*{st.session_state['user_data']['branch']} | Sem {st.session_state['user_data']['semester']}*")
        st.divider()
        
        selection = st.radio("Navigation", [
            "Dashboard",
            "Update Attendance", 
            "Safe Holiday Calculator",
            "Future Predictor",
            "AI Advisor & Career",
            "Wellness Chatbot",
            "Profile Settings"
        ])
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_data'] = None
            st.rerun()

    # Routing
    if selection == "Dashboard":
        st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
        import dashboard
        dashboard.render()
        
    elif selection == "Update Attendance":
        st.markdown('<div class="main-header">Attendance Input</div>', unsafe_allow_html=True)
        import attendance_parser
        attendance_parser.render()
        
    elif selection == "Safe Holiday Calculator":
        st.markdown('<div class="main-header">Safe Holidays</div>', unsafe_allow_html=True)
        import safe_holiday
        safe_holiday.render()
        
    elif selection == "Future Predictor":
        st.markdown('<div class="main-header">Attendance Predictor</div>', unsafe_allow_html=True)
        import predictor
        predictor.render()
        
    elif selection == "AI Advisor & Career":
        st.markdown('<div class="main-header">AI Career & Advice</div>', unsafe_allow_html=True)
        import career_advisor
        career_advisor.render()
        
    elif selection == "Wellness Chatbot":
        st.markdown('<div class="main-header">Wellness Assistant</div>', unsafe_allow_html=True)
        import chatbot
        chatbot.render()
        
    elif selection == "Profile Settings":
        st.markdown('<div class="main-header">Profile Settings</div>', unsafe_allow_html=True)
        st.write("### Your Information")
        st.json(st.session_state['user_data'])
        st.info("Additional profile settings like password reset can be added here.")

# --- Router ---
if not st.session_state['logged_in']:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login_page()
    with tab2:
        register_page()
else:
    main_app()