import datetime

def get_greeting():
    """Returns a time-based greeting."""
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good Morning"
    elif 12 <= current_hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"