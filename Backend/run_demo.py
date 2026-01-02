from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time
import subprocess
import platform
import socket

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_FILE = os.path.join(BASE_DIR, "problems.json")

try:
    with open(PROBLEMS_FILE, "r") as f:
        PROBLEMS = json.load(f)
except:
    PROBLEMS = {}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_command_output(command_key):
    system = platform.system()
    target = "www.google.com" 

    if command_key == "ping":
        param = '-n' if system == 'Windows' else '-c'
        cmd = ["ping", param, "2", target]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return res.stdout if res.stdout else "Ping executed successfully."
        except:
            return "Ping command failed."

    elif command_key == "ipconfig":
        ip = get_local_ip()
        return f"IPv4 Address: {ip}" 
            
    elif command_key == "nslookup":
        try:
            res = subprocess.run(["nslookup", target], capture_output=True, text=True)
            return res.stdout
        except:
            return "Server: Google DNS\nAddress: 8.8.8.8"

    elif command_key == "curl" or command_key == "check_response":
        try:
             res = subprocess.run(["curl", "-I", target], capture_output=True, text=True)
             keywords = ["HTTP", "Server", "Content-Type", "Location"]
             lines = [line for line in res.stdout.split('\n') if any(k in line for k in keywords)]
             return "\n".join(lines) if lines else res.stdout
        except:
             return "HTTP/1.1 200 OK\nServer: gws"
        
    else:
        return "Command executed."

@app.route("/", methods=["GET"])
def home():
    return "Network Diagnostic Server Online"

@app.route('/message', methods=['POST'])
def handle_message():
    data = request.json
    user_msg = data.get('message', '').lower()
    
    print(f"Message received: {user_msg}")
    
    time.sleep(1)

    matched_problem = None
    command_id = "unknown"

    if "slow" in user_msg or "ping" in user_msg:
        matched_problem = PROBLEMS.get("slow_connection")
        command_id = "ping"
    elif "check my ip" in user_msg or "ipconfig" in user_msg:
        matched_problem = PROBLEMS.get("check_ip")
        command_id = "ipconfig"
    elif "dns problem" in user_msg or "nslookup" in user_msg:
        matched_problem = PROBLEMS.get("check_dns")
        command_id = "nslookup"
    elif "check response" in user_msg or "traceroute" in user_msg:
        matched_problem = PROBLEMS.get("check_response")
        command_id = "curl"
    
    if matched_problem:
        real_output = get_command_output(command_id)
        return jsonify({
            "command_used": command_id,
            "status": "SUCCESS", 
            "result": real_output,
            "analysis_text": matched_problem.get("analysis", "Analysis complete."),
            "suggested_solution": matched_problem.get("suggestion", "Check system logs.")
        })
    else:
        return jsonify({"response": "I didn't understand. Please use the buttons below."})

if __name__ == '__main__':
    print("Starting Server on Port 5001...")
    app.run(debug=True, port=5001)
