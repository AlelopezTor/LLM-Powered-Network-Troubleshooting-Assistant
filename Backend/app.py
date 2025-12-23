from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import platform
import subprocess

app = Flask(__name__)
CORS(app)  # permite conexión desde frontend

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


@app.route("/", methods=["GET"])
def home():
    return "Backend Flask with Ollama working"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    payload = {"model": MODEL, "prompt": user_message, "stream": False}
    response = requests.post(OLLAMA_URL, json=payload)
    llm_response = response.json()["response"]

    return jsonify({"response": llm_response})

@app.route("/run", methods=["POST"])
def run():
    data = request.json
    user_message = data.get("command")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    system = platform.system()
    commands = {
        "ping": ["ping", "google.com", "-n", "4"] if system == "Windows" else ["ping", "-c", "4", "google.com"],
        "ipconfig": ["ipconfig"] if system == "Windows" else ["ifconfig"],
        "traceroute": ["tracert", "google.com"] if system == "Windows" else ["traceroute", "google.com"]
    }
    if user_message not in commands:
        return jsonify({"error": "Command not supported"}), 400

    try:
        result = subprocess.run(commands[user_message], capture_output=True, text=True, timeout=20)
        return jsonify({
            "command": user_message,
            "output": result.stdout
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
