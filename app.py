from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
import os, json, requests
from uuid import uuid4
from datetime import datetime
from langdetect import detect
from googletrans import Translator
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = str(uuid4())
CORS(app)

USERS_FILE = "users.json"
CHAT_LOG_DIR = "chats"
MODEL_NAME = "gemma:2b"
translator = Translator()
user_sessions = {}

# Ensure directories
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)
if not os.path.exists(CHAT_LOG_DIR):
    os.makedirs(CHAT_LOG_DIR)

# Utility: translate if needed
def translate_to_english(text):
    try:
        lang = detect(text)
        if lang != "en":
            return translator.translate(text, dest="en").text
        return text
    except:
        return text

# Utility: log chat to file
def save_chat(username, prompt, response):
    file_path = os.path.join(CHAT_LOG_DIR, f"{username}_{datetime.now().date()}.txt")
    with open(file_path, "a") as f:
        f.write(f"You: {prompt}\nAI: {response}\n\n")

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        with open(USERS_FILE, "r+") as f:
            users = json.load(f)
            if username in users:
                return "User already exists. Go back and try again."
            users[username] = password
            f.seek(0)
            json.dump(users, f)
            f.truncate()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open(USERS_FILE) as f:
            users = json.load(f)
            if username in users and check_password_hash(users[username], password):
                session['username'] = username
                if username not in user_sessions:
                    user_sessions[username] = []
                return redirect(url_for('chat'))
            return "Invalid credentials."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html')

@app.route('/stream', methods=['POST'])
def stream():
    if 'username' not in session:
        return "Unauthorized", 401

    username = session['username']
    prompt = request.json.get('message', '')
    personality = request.json.get('personality', 'You are a helpful assistant.')
    translated_input = translate_to_english(prompt)
    history = user_sessions.get(username, [])

    def generate():
        context = "\n".join([f"User: {h[0]}\nAI: {h[1]}" for h in history])
        full_prompt = f"{personality}\n{context}\nUser: {translated_input}\nAI:"
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": MODEL_NAME, "prompt": full_prompt, "stream": True},
            stream=True
        )
        collected = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    token = data.get("response", "")
                    collected += token
                    yield f"data: {token}\n\n"
                except:
                    continue
        user_sessions[username].append((prompt, collected))
        save_chat(username, prompt, collected)

    return Response(generate(), mimetype='text/event-stream')

@app.route('/clear')
def clear():
    username = session.get("username")
    if username in user_sessions:
        user_sessions[username] = []
    return redirect(url_for('chat'))

@app.route('/logs')
def logs():
    if 'username' not in session:
        return jsonify([])

    username = session['username']
    files = os.listdir(CHAT_LOG_DIR)
    user_logs = [f for f in files if f.startswith(username)]
    return jsonify(user_logs)

# Run app
if __name__ == '__main__':
    app.run(debug=True)
