import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Database Configuration
DATABASE_URL = "sqlite:///attendance_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Models ---

class User(Base):
    __tablename__ = "users"
    
    student_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attendance_records = relationship("AttendanceHistory", back_populates="user", cascade="all, delete-orphan")
    chat_records = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")


class AttendanceHistory(Base):
    __tablename__ = "attendance_history"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.student_id"))
    subject = Column(String, nullable=False)
    classes_present = Column(Integer, nullable=False)
    total_classes = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="attendance_records")


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.student_id"))
    role = Column(String, nullable=False) # 'user' or 'model'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_records")


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.student_id"))
    subject = Column(String, nullable=False)
    predicted_attendance_5 = Column(Float)
    predicted_attendance_10 = Column(Float)
    predicted_attendance_20 = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.student_id"))
    ai_suggestion = Column(Text, nullable=False)
    type = Column(String) # e.g., 'Attendance', 'Career', 'Wellness'
    generated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")


def init_db():
    """Creates all tables in the database if they don't exist."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()