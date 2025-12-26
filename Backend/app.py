from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import platform
import subprocess
import json
import os
import re
app = Flask(__name__)
CORS(app) 
conversation_history = []
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


@app.route("/", methods=["GET"])
def home():
    return "Backend Flask with Ollama working"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "problems.json"), "r") as f:
    PROBLEMS = json.load(f)
    
def is_diagnostic_message(text):
    diagnostic_keys = []
    for problem in PROBLEMS.values():
        diagnostic_keys.extend(problem["keywords"])
    for kw in diagnostic_keys:
        if kw in text: 
            return True
    return False
        
        
def chat(user_text):
    if not user_text:
        return jsonify({"error": "No message provided"}), 400    
    prompt = f"""
    You are an assistant that helps diagnose network problems.
    Given the user's message, return only a JSON NO MORE TEXT.
    These are the available commands you can choose: ping (internet problems, slow internet), ipconfig(check my ip),
    nslookup(dns), nc(firewall), curl(rate limit and check/see response from a server).CHOOSE ONLY ONE, ONLY ONE CAN BE EXECUTED
    Return the response strictly as JSON **with no extra text or formatting** and only with the following fields:
    {{
        "suggested_command": "<command_to_execute_only_the_command_name_ONLY_ONE>",
        "analysis_text": "<short_explanation_for_user>",
        "suggested_solution": "<short_explanation_for_a_solution>",
        "url": "none or full URL(mandatory for curl)",
        "host": "none or hostname(mandatory for nslookup, nc)",
        "port": "none or port number(mandatory for firewall)"
    }}
    If you cannot determine the correct values, use a random URL, host, or port if its mandatory, and empty strings for analysis/solution.
    ONLY RETURN JSON, nothing else(NO TEXT).
    User message: {user_text}
    """
    
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    response = requests.post(OLLAMA_URL, json=payload)
    response_text = response.json()["response"]
    match = re.search(r'\{.*?\}', response_text, re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            llm_response = json.loads(json_text)
        except json.JSONDecodeError:
            llm_response = {
                "suggested_command": "none",
                "analysis_text": "",
                "suggested_solution": "",
                "url": "none",
                "host": "none",
                "port": "none"
            }
    else:
        llm_response = {
            "suggested_command": "none",
            "analysis_text": "",
            "suggested_solution": "",
            "url": "none",
            "host": "none",
            "port": "none"
        }


    url = None
    host = None
    port = None
    if llm_response["url"] != "none":
        url = llm_response["url"]
    elif llm_response["host"] != "none":
        host = llm_response["host"]
    elif llm_response["port"] != "none":
        port = llm_response["port"]
    response = assistant(user_text, url, host, port, llm_response, found = is_diagnostic_message(user_text))
    if isinstance(response, tuple):
        response_obj = response[0]
        status_code = response[1]
    else:
        response_obj = response
        status_code = 200
    if status_code != 200:
        return response
    data_for_ai = response_obj.get_json()
    result = json.dumps(data_for_ai, indent=2)
    prompt2 = f"""
        You are a network expert. Analyze the following command execution result:
        {result}

        Decide if the connection is successful or failing based on the 'raw_output'.
        Return ONLY a JSON with these fields:
        {{
            "command_used": "{data_for_ai.get('command_executed')}",
            "status": "success or failure",
            "result": "working or not working",
            "analysis_text": "short explanation of the terminal output",
            "suggested_solution": "what the user should do" 
        }}
        ONLY RESPOND WITH JSON.
        """
    
    payload = {"model": MODEL, "prompt": prompt2, "stream": False}
    response = requests.post(OLLAMA_URL, json=payload)
    response_text = response.json()["response"]
    match = re.search(r'\{.*?\}', response_text, re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            llm_response_final = json.loads(json_text)
        except json.JSONDecodeError:
            llm_response_final = {
                "suggested_command": "none",
                "analysis_text": "",
                "suggested_solution": "",
                "url": "none",
                "host": "none",
                "port": "none"
            }
    else:
        llm_response_final = {
            "suggested_command": "none",
            "analysis_text": "",
            "suggested_solution": "",
            "url": "none",
            "host": "none",
            "port": "none"
        }
    return llm_response_final

def assistant(user_text, url, host, port, llm_response, found = True):

    if not user_text:
        return jsonify({"error": "No message provided"}), 400
    selected_problem = None
    if found:
        for problem_data in PROBLEMS.values():
            for kw in problem_data["keywords"]:
                if kw in user_text:
                    selected_problem = problem_data
                    break

        if not selected_problem:
            return jsonify({
                "response": "I could not identify the problem. Please describe it more clearly."
            })
            
        if selected_problem["command"] not in llm_response["suggested_command"]:
            return jsonify({
                "response1": selected_problem["command"],
                "response2": llm_response["suggested_command"]
            })
        command = selected_problem["command"]
    else:        
        command = llm_response.get("suggested_command", "").strip()
                    
    
    system = platform.system()
    
    if command == "nslookup" and host == None:
        return jsonify({
            "response": "I could not identify the host. Please describe it more clearly."
        })
    elif (command == "nc" ):
        if host == None:
            return jsonify({
                "response": "I could not identify the host. Please describe it more clearly."
            })
        elif port == None:
            return jsonify({
            "response": "I could not identify the port. Please describe it more clearly."
        })    
    elif command == "curl" and url == None:
        return jsonify({
            "response": "I could not identify url. Please describe it more clearly."
        })
        
    commands = {
        "ping": ["ping", "google.com", "-n", "4"] if system == "Windows" else ["ping", "-c", "4", "google.com"],
        "ipconfig": ["ipconfig"] if system == "Windows" else ["ifconfig"],
        "nslookup": ["nslookup", host],
        "nc": ["nc", "-zv", host, port],
        "curl": ["curl", "-v", url] 
    }
    
    result = subprocess.run(
        commands[command],
        capture_output=True,
        text=True,
        timeout=20
    )

    output = result.stdout.lower()
    status = "OK"

    if "timed out" in output or "unreachable" in output:
        status = "ERROR"
    elif "ms" in output:
        status = "OK"
    else:
        status = "WARNING"
        
    if found and selected_problem:   
        conversation_history.append({
        "user": user_text,
        "command": command,
        "analysis": selected_problem["analysis"],
        "suggestion": selected_problem["suggestion"]
        })
    else:
        conversation_history.append({
        "user": user_text,
        "command": command,
        "analysis": llm_response["analysis_text"],
        "suggestion": llm_response["suggested_solution"]
        })
    
    if found and selected_problem:   
        return jsonify({
            "detected_problem": command,
            "command_executed": command,
            "status": status,
            "analysis": selected_problem["analysis"],
            "suggestion": selected_problem["suggestion"],
            "raw_output": result.stdout
            })
    else:
        return jsonify({
        "detected_problem": command,
        "command_executed": command,
        "status": status,
        "analysis": llm_response["analysis_text"],
        "suggestion": llm_response["suggested_solution"],
        "raw_output": result.stdout
        })
    
@app.route("/history", methods= ["GET"])
def history():
    return jsonify(conversation_history)

@app.route("/message", methods=["POST"])
def message():
    user_text = request.json.get("message", "").lower()

    if not user_text:
        return jsonify({"error": "No message provided"}), 400
    result = chat(user_text)

    return result
if __name__ == "__main__":
    app.run(debug=True)
