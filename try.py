from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
import uvicorn
import openai
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import os
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI()

# OpenAI API Key (Set your API key as an environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user database (Replace with real database in production)
users_db = {}
user_settings_db = {}

class User(BaseModel):
    username: str
    password: str

class UserInfo(BaseModel):
    username: str
    full_name: str
    email: str

class UserSettings(BaseModel):
    username: str
    theme: str
    notifications: bool

@app.post("/register")
async def register(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = pwd_context.hash(user.password)
    users_db[user.username] = hashed_password
    user_settings_db[user.username] = {"theme": "light", "notifications": True}
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(user: User):
    if user.username not in users_db or not pwd_context.verify(user.password, users_db[user.username]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful"}

@app.post("/update_user_info")
async def update_user_info(user_info: UserInfo):
    if user_info.username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    users_db[user_info.username] = {
        "full_name": user_info.full_name,
        "email": user_info.email
    }
    return {"message": "User information updated successfully"}

@app.get("/user_info")
async def get_user_info(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[username]

@app.post("/update_settings")
async def update_settings(settings: UserSettings):
    if settings.username not in user_settings_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_settings_db[settings.username] = {
        "theme": settings.theme,
        "notifications": settings.notifications
    }
    return {"message": "Settings updated successfully"}

@app.get("/settings")
async def get_settings(username: str):
    if username not in user_settings_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_settings_db[username]

@app.post("/scan_medicine")
async def scan_medicine(file: UploadFile = File(...)):
    # Read image
    image = Image.open(io.BytesIO(await file.read()))
    image = np.array(image)
    
    # OCR for Text Recognition using Tesseract
    extracted_text = pytesseract.image_to_string(image)
    
    # Query OpenAI for Authenticity Check
    prompt = (
        f"Check the authenticity of the following medicine details: {extracted_text}. "
        "Verify if all ingredients match the known composition of the medicine, "
        "check the expiry date for validity, and confirm if it is approved by FDA, WHO, and CDSCO. "
        "Provide a detailed response on whether the medicine is authentic or potentially counterfeit."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    authenticity_status = response["choices"][0]["message"]["content"].strip()
    
    return {"medicine": extracted_text, "status": authenticity_status}

@app.get("/search_medicine")
async def search_medicine(name: str = Form(...)):
    # Query OpenAI for Medicine Information
    prompt = (
        f"Provide details about the medicine named {name}. "
        "Include composition, uses, side effects, and regulatory approval status."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    medicine_info = response["choices"][0]["message"]["content"].strip()
    
    return {"medicine": name, "details": medicine_info}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
