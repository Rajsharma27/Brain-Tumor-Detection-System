import json
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from src.database.db_model import Base
from datetime import datetime



class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    symptoms = Column(Text)
    prediction = Column(String)
    confidence = Column(Float)