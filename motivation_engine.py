import random
import streamlit as st

def get_motivation_quote():
    """Returns a random motivational quote for students."""
    quotes = [
        "The future depends on what you do today. – Mahatma Gandhi",
        "Success is the sum of small efforts, repeated day in and day out. – Robert Collier",
        "Don't watch the clock; do what it does. Keep going. – Sam Levenson",
        "Education is the most powerful weapon which you can use to change the world. – Nelson Mandela",
        "It always seems impossible until it is done. – Nelson Mandela",
        "Strive for progress, not perfection. – Unknown"
    ]
    return random.choice(quotes)

def render_motivation_ui():
    """Renders the motivation component in Streamlit."""
    quote = get_motivation_quote()
    st.markdown(f"""
        <div style="background-color: #1E2127; padding: 1rem; border-radius: 8px; border-left: 4px solid #F5A623; margin-top: 1rem; margin-bottom: 1rem;">
            <p style="font-size: 1.1rem; font-style: italic; margin: 0;">💡 "{quote}"</p>
        </div>
    """, unsafe_allow_html=True)