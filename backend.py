from flask import Flask, request, jsonify
import sqlite3
import random
import string
from captcha.image import ImageCaptcha

app = Flask(__name__)

# Database Initialization
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (name TEXT, phone TEXT PRIMARY KEY, password TEXT, age TEXT, 
                   sex TEXT, blood_group TEXT, weight TEXT, height TEXT, medical_history TEXT, first_login INTEGER)''')
conn.commit()

# Generate Captcha
def generate_captcha():
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    image = ImageCaptcha()
    image_path = f"static/{captcha_text}.png"
    image.write(captcha_text, image_path)
    return captcha_text, image_path

@app.route('/get_captcha', methods=['GET'])
def get_captcha():
    captcha_text, image_path = generate_captcha()
    return jsonify({"captcha_text": captcha_text, "captcha_image": image_path})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (data['name'], data['phone'], data['password'], "", "", "", "", "", "", 1))
        conn.commit()
        return jsonify({"message": "Registration Successful"}), 200
    except:
        return jsonify({"error": "User already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    cursor.execute("SELECT * FROM users WHERE phone=? AND password=?", (data['phone'], data['password']))
    user = cursor.fetchone()
    if user:
        return jsonify({"message": "Login Successful", "first_login": user[-1]}), 200
    return jsonify({"error": "Invalid Credentials"}), 401

@app.route('/update_info', methods=['POST'])
def update_info():
    data = request.json
    cursor.execute('''UPDATE users SET age=?, sex=?, blood_group=?, weight=?, height=?, medical_history=?, first_login=0 
                      WHERE phone=?''',
                   (data['age'], data['sex'], data['blood_group'], data['weight'], data['height'], data['medical_history'], data['phone']))
    conn.commit()
    return jsonify({"message": "Information Updated"}), 200

if __name__ == "__main__":
    app.run(debug=True)
