from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    phone_number = Column(String, primary_key=True, index=True, unique=True)
    hashed_password = Column(String)
