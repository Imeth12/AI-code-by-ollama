# AI-code-by-ollama
this is an ai created by the co-operation with ollama
## 🚀 How to Run This AI Chatbot App Locally

Follow these steps to run the app on your computer:

### 1. Clone the repository

bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2. Create a virtual environment (optional but recommended)

bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install dependencies
bash

pip install -r requirements.txt

4. Start Ollama and load a model (e.g. Gemma or Mistral)
Make sure you have Ollama installed.

ollama run gemma
5. Start the Flask app

python app.py
6. Open in your browser
Visit: http://localhost:5000

✨ Features
Login and register system 🔐

Streaming AI responses 🧠

Voice input + speech output 🎙

Dark mode toggle 🌙
📂 Project Structure
pgsql
Copy
Edit
AI-code-by-ollama/
├── app.py
├── requirements.txt
├── templates/
│   ├── chat.html
│   ├── login.html
│   └── register.html
├── static/
│   ├── style.css
│   ├── user.png
│   └── ai.png
└── README.md

Google tools bar (Gmail, Calendar, etc.)

Markdown formatting and history logs

Avatar support for chat bubbles
