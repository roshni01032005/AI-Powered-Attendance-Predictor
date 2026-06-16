import pandas as pd

def calculate_subject_wise(df):
    """Calculates percentage for each subject."""
    if df.empty:
        return df
    # Prevent division by zero
    df['Total'] = df['Total'].replace(0, 1) 
    df['Percentage'] = (df['Present'] / df['Total']) * 100
    df['Percentage'] = df['Percentage'].round(2)
    return df

def calculate_overall(df):
    """Calculates overall attendance percentage."""
    if df.empty:
        return 0.0
    total_present = df['Present'].sum()
    total_classes = df['Total'].sum()
    
    if total_classes == 0:
        return 0.0
    return round((total_present / total_classes) * 100, 2)

def get_attendance_status(percentage):
    """Returns a status string and UI color based on attendance %."""
    if percentage >= 85:
        return "Excellent", "normal"
    elif percentage >= 75:
        return "Safe", "normal"
    elif percentage >= 65:
        return "Warning", "off" 
    else:
        return "Critical", "inverse"