from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # permite conexión desde frontend

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


@app.route("/", methods=["GET"])
def home():
    return "Backend Flask con Ollama funcionando 🚀"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    payload = {
        "model": MODEL,
        "prompt": user_message,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        llm_response = response.json()["response"]

        return jsonify({
            "response": llm_response
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
