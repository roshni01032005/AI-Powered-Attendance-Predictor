import bcrypt
from sqlalchemy.orm import Session
from database import User

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(db: Session, student_id: str, name: str, email: str, password: str, branch: str, semester: int):
    """Registers a new user in the database."""
    # Check if user already exists
    existing_user = db.query(User).filter((User.student_id == student_id) | (User.email == email)).first()
    if existing_user:
        return False, "Student ID or Email already exists."

    hashed_pw = hash_password(password)
    new_user = User(
        student_id=student_id,
        name=name,
        email=email,
        password=hashed_pw,
        branch=branch,
        semester=semester
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return True, "Registration successful."
    except Exception as e:
        db.rollback()
        return False, f"Database error: {str(e)}"

def authenticate_user(db: Session, student_id: str, password: str):
    """Authenticates a user and returns the user object if successful."""
    user = db.query(User).filter(User.student_id == student_id).first()
    if not user:
        return False, "Invalid Student ID."
    
    if not verify_password(password, user.password):
        return False, "Invalid password."
        
    return True, user