from flask import Flask, request, jsonify
import openai
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import os
from passlib.context import CryptContext

app = Flask(__name__)

# OpenAI API Key (Set your API key as an environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user database (Replace with real database in production)
users_db = {}
user_settings_db = {}

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if username in users_db:
        return jsonify({"error": "Username already exists"}), 400
    
    hashed_password = pwd_context.hash(password)
    users_db[username] = hashed_password
    user_settings_db[username] = {"theme": "light", "notifications": True}
    return jsonify({"message": "User registered successfully"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if username not in users_db or not pwd_context.verify(password, users_db[username]):
        return jsonify({"error": "Invalid username or password"}), 401
    
    return jsonify({"message": "Login successful"})

@app.route("/scan_medicine", methods=["POST"])
def scan_medicine():
    file = request.files["file"]
    image = Image.open(io.BytesIO(file.read()))
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
    
    return jsonify({"medicine": extracted_text, "status": authenticity_status})

@app.route("/search_medicine", methods=["POST"])
def search_medicine():
    data = request.json
    name = data.get("name")
    
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
    
    return jsonify({"medicine": name, "details": medicine_info})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
