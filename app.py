import os
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))
CORS(app)

JOKES_DATABASE = []

def load_jokes():
    """Load the frozen jokes database from JSON file."""
    global JOKES_DATABASE
    try:
        db_path = os.path.join(base_dir, "jokes_database.json")
        with open(db_path, "r") as f:
            JOKES_DATABASE = json.load(f)
        print(f"✓ Loaded {len(JOKES_DATABASE)} jokes from database")
        return True
    except FileNotFoundError:
        print("❌ jokes_database.json not found.")
        return False

def format_jokes_for_context():
    """Format jokes for LLM context — natural language only, no raw keys exposed."""
    lines = []
    for i, joke in enumerate(JOKES_DATABASE, 1):
        category = joke.get("category", "General")
        if joke.get("type") == "single":
            lines.append(f"[{i}] ({category}) {joke.get('joke', '')}")
        else:
            setup = joke.get("setup", "")
            delivery = joke.get("delivery", "")
            lines.append(f"[{i}] ({category}) {setup} — {delivery}")
    return "\n".join(lines)

def query_openrouter(user_query):
    """Send query to OpenRouter with grounded context."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "OpenRouter API key not configured"}

    jokes_context = format_jokes_for_context()

    system_prompt = f"""You are a friendly joke assistant. You have access to a curated database of jokes listed below.
    DATABASE:{jokes_context}

    RULES:
    1. Only use jokes from the database — never invent new ones.
    2. When sharing jokes, tell them naturally and conversationally. For two-part jokes, present the setup as a question and the punchline on a new line — do NOT mention "setup", "delivery", "category", or any database field names.
    3. Share at most 2–3 jokes per response unless the user explicitly asks for more.
    4. If the user asks for a specific topic, pick the best matching jokes — don't dump every match.
    5. Refuse any requests for NSFW, offensive, or off-topic content politely.
    6. Keep responses warm, brief, and fun."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:8080",
            },
            json={
                "model": "anthropic/claude-3-haiku",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 400,
            }
        )
        if response.status_code != 200:
            return {"error": f"OpenRouter error: {response.status_code}"}

        data = response.json()
        return {
            "answer": data["choices"][0]["message"]["content"],
            "model": "anthropic/claude-3-haiku",
            "status": "success"
        }
    except Exception as e:
        return {"error": f"Error querying OpenRouter: {str(e)}"}

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html')

@app.route("/chat", methods=["POST"])
def chat():
    if not JOKES_DATABASE:
        return jsonify({"error": "Joke database not loaded"}), 500

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data.get("message", "").strip()
    result = query_openrouter(user_message)
    return jsonify(result)

if __name__ == "__main__":
    load_jokes()
    app.run(debug=True, host="0.0.0.0", port=8080)