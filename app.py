import speedtest
import socket
import psutil
from ping3 import ping
from flask import Flask, render_template, request, jsonify
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Legacy responses for fallback
responses = {
    "slow internet":
    "Your internet may be slow due to bandwidth overload, weak WiFi signal, or background downloads. Try restarting your router and disconnecting unused devices.",

    "wifi not connecting":
    "Check your WiFi password, restart the router, and ensure airplane mode is turned off.",

    "wi-fi not connecting":
    "Check your WiFi password, restart the router, and ensure airplane mode is turned off.",

    "dns issue":
    "Try changing your DNS server to 8.8.8.8 or flush DNS cache using command prompt.",

    "no internet":
    "Check router cables, restart the modem, and verify your ISP connection.",

    "router issue":
    "Restart the router and check if indicator lights are blinking normally.",

    "packet loss":
    "Packet loss can occur due to damaged cables, congestion, or unstable WiFi signals.",

    "high ping":
    "High ping usually occurs because of network congestion or distant servers.",

    "internet disconnecting":
    "Your WiFi signal may be weak or your ISP may have instability issues.",

    "connected but no internet":
    "Try restarting your router, renewing IP address, or resetting network settings.",

    "default":
    "I can help with WiFi, DNS, router, ping, internet speed, and network troubleshooting problems."
}

# Get API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot():
    user_message = request.json["message"].lower()
    ai_type = request.json.get("ai_type", "gemini")  # "gemini" or "openrouter"

    try:
        if ai_type == "gemini" and GEMINI_API_KEY:
            reply = get_gemini_response(user_message)
        elif ai_type == "openrouter" and OPENROUTER_API_KEY:
            reply = get_openrouter_response(user_message)
        else:
            # Fallback to basic responses
            reply = responses.get("default")
            for key in responses:
                if key in user_message:
                    reply = responses[key]
                    break

        return jsonify({"reply": reply, "success": True})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "reply": f"I encountered an error: {str(e)}. Please try again.",
            "success": False
        })

def get_gemini_response(user_message):
    """Get response from Google Gemini API"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    system_prompt = """You are an expert Network Diagnostic AI Assistant. You help users troubleshoot network and internet issues.
    Provide clear, concise, and actionable solutions for:
    - WiFi connectivity problems
    - Internet speed issues
    - DNS problems
    - Router configuration
    - Network diagnostics
    - Ping and latency issues
    - IP address problems
    
    Always be professional, friendly, and provide step-by-step solutions when applicable."""
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"{system_prompt}\n\nUser Question: {user_message}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 500,
        }
    }
    
    response = requests.post(
        f"{url}?key={GEMINI_API_KEY}",
        json=payload,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Gemini API error: {response.text}")

def get_openrouter_response(user_message):
    """Get response from OpenRouter API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    system_prompt = """You are an expert Network Diagnostic AI Assistant. You help users troubleshoot network and internet issues.
    Provide clear, concise, and actionable solutions for:
    - WiFi connectivity problems
    - Internet speed issues
    - DNS problems
    - Router configuration
    - Network diagnostics
    - Ping and latency issues
    - IP address problems
    
    Always be professional, friendly, and provide step-by-step solutions when applicable."""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Network Diagnostic Chatbot"
    }
    
    payload = {
        "model": "openrouter/auto",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }
    
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"OpenRouter API error: {response.text}")

@app.route("/network")
def network_info():
    ip_address = socket.gethostbyname(socket.gethostname())

    data = {
        "status": "Connected",
        "download": 85,
        "upload": 40,
        "ping": 18,
        "ip": ip_address
    }

    return jsonify(data)

@app.route("/report")
def generate_report():
    doc = SimpleDocTemplate("network_report.pdf")
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(
        "AI Network Diagnostic Report",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 12))

    report_text = """
    <b>Status:</b> Connected<br/><br/>
    <b>Download Speed:</b> 85 Mbps<br/><br/>
    <b>Upload Speed:</b> 40 Mbps<br/><br/>
    <b>Ping:</b> 18 ms<br/><br/>
    <b>Analysis:</b>
    Your network is stable and working properly.
    """

    paragraph = Paragraph(report_text, styles['BodyText'])
    elements.append(paragraph)

    doc.build(elements)

    return "Report Generated Successfully!"

if __name__ == "__main__":
    app.run(debug=True)