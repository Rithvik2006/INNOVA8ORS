from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from .models import User
from .utils import hash_password
from pydantic import BaseModel

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schema for request validation
class UserCreate(BaseModel):
    phone_number: str
    password: str

@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.phone_number == user.phone_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create new user
    new_user = User(phone_number=user.phone_number, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    
    return {"message": "User registered successfully"}
