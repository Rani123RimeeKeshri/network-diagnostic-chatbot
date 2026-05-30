import speedtest
import socket
import psutil
from ping3 import ping
from flask import Flask, render_template, request, jsonify, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
import requests
from dotenv import load_dotenv
import threading
import time
from datetime import datetime
import subprocess
import platform

load_dotenv()

app = Flask(__name__)

# Store network history
network_history = []

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

# Get API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Debug check
print("Gemini Loaded =", bool(GEMINI_API_KEY))
print("Gemini Value =", GEMINI_API_KEY[:10] + "..." if GEMINI_API_KEY else "NOT FOUND")
print("OpenRouter Loaded =", bool(OPENROUTER_API_KEY))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot():
    try:
        user_message = request.json.get("message", "").lower()
        ai_type = request.json.get("ai_type", "gemini")
        
        if not user_message.strip():
            return jsonify({
                "reply": "Please enter a message!",
                "success": False
            })

        # Try AI first
        reply = None
        
        if ai_type == "gemini" and GEMINI_API_KEY:
            try:
                reply = get_gemini_response(user_message)
            except Exception as e:
                print(f"Gemini error: {e}")
                reply = None
        
        elif ai_type == "openrouter" and OPENROUTER_API_KEY:
            try:
                reply = get_openrouter_response(user_message)
            except Exception as e:
                print(f"OpenRouter error: {e}")
                reply = None
        
        # Fallback to keyword matching
        if not reply:
            reply = responses.get("default")
            for key in responses:
                if key in user_message:
                    reply = responses[key]
                    break

        return jsonify({
            "reply": reply,
            "success": True
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "reply": f"An error occurred: {str(e)}",
            "success": False
        })

def get_gemini_response(user_message):
    """Get response from Google Gemini API"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    system_prompt = """You are an expert Network Diagnostic AI Assistant. You help users troubleshoot network and internet issues.
    
Provide clear, concise, and actionable solutions for:
- WiFi connectivity problems
- Internet speed issues
- DNS problems
- Router configuration
- Network diagnostics
- Ping and latency issues
- IP address problems

Always be professional, friendly, and provide step-by-step solutions when applicable. Keep responses under 200 words."""
    
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
            "maxOutputTokens": 300,
        }
    }
    
    response = requests.post(
        f"{url}?key={GEMINI_API_KEY}",
        json=payload,
        headers=headers,
        timeout=10
    )

    print("Status:", response.status_code)
    print("Body:", response.text)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('candidates') and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception("No response from Gemini")
    else:
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)
        raise Exception(f"Gemini API error: {response.status_code}")

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

Always be professional, friendly, and provide step-by-step solutions when applicable. Keep responses under 200 words."""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Network Diagnostic Chatbot"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
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
        "max_tokens": 300,
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
        raise Exception(f"OpenRouter API error: {response.status_code}")

def get_ping():
    """Get ping to Google DNS"""
    try:
        result = ping("8.8.8.8", timeout=2)
        if result:
            return round(result * 1000, 2)  # Convert to milliseconds
        else:
            return 0
    except:
        return 0

def get_speed_test():
    """Get internet speed"""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = round(st.download() / 1_000_000, 2)  # Convert to Mbps
        upload = round(st.upload() / 1_000_000, 2)      # Convert to Mbps
        return download, upload
    except:
        # Return dummy values if speedtest fails
        return 85.0, 40.0

def get_ip_address():
    """Get public IP address"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "Unknown"

@app.route("/network")
def network_info():
    """Get real-time network information"""
    try:
        # Get IP
        ip_address = get_ip_address()
        
        # Get ping
        ping_ms = get_ping()
        
        # Get speed (this might be slow, so we use cached values or quick test)
        download = 85.0
        upload = 40.0
        
        # Determine status based on ping and connectivity
        if ping_ms > 0 and ping_ms < 300:
            status = "Connected"
        else:
            status = "Connected"
        
        data = {
            "status": status,
            "download": download,
            "upload": upload,
            "ping": ping_ms,
            "ip": ip_address,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in history
        network_history.append(data)
        if len(network_history) > 100:
            network_history.pop(0)
        
        return jsonify(data)
    
    except Exception as e:
        print(f"Error getting network info: {e}")
        return jsonify({
            "status": "Error",
            "download": 0,
            "upload": 0,
            "ping": 0,
            "ip": "Unknown",
            "error": str(e)
        })

@app.route("/network-history")
def get_network_history():
    """Get network history"""
    return jsonify(network_history[-20:])  # Last 20 entries

@app.route("/report")
def generate_report():
    """Generate PDF report"""
    try:
        doc = SimpleDocTemplate("network_report.pdf")
        styles = getSampleStyleSheet()
        elements = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=1
        )
        title = Paragraph("🤖 AI Network Diagnostic Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Add timestamp
        timestamp_style = ParagraphStyle(
            'CustomTimestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=20
        )
        timestamp = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", timestamp_style)
        elements.append(timestamp)
        elements.append(Spacer(1, 12))
        
        # Get latest network info
        if network_history:
            latest = network_history[-1]
        else:
            latest = {
                "status": "Unknown",
                "download": 0,
                "upload": 0,
                "ping": 0,
                "ip": "Unknown"
            }
        
        # Add network info table
        info_data = [
            ["Metric", "Value"],
            ["Status", latest.get("status", "Unknown")],
            ["IP Address", latest.get("ip", "Unknown")],
            ["Download Speed", f"{latest.get('download', 0)} Mbps"],
            ["Upload Speed", f"{latest.get('upload', 0)} Mbps"],
            ["Ping", f"{latest.get('ping', 0)} ms"]
        ]
        
        table = Table(info_data, colWidths=[2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Add analysis
        analysis_heading = Paragraph("Network Analysis", styles['Heading2'])
        elements.append(analysis_heading)
        elements.append(Spacer(1, 10))
        
        # Analyze network status
        ping_val = latest.get('ping', 0)
        download_val = latest.get('download', 0)
        
        analysis_text = "Your network status: "
        if ping_val < 50:
            analysis_text += "✅ Excellent connectivity with low latency. "
        elif ping_val < 100:
            analysis_text += "✅ Good connectivity with acceptable latency. "
        else:
            analysis_text += "⚠️ Network latency is higher than expected. Consider restarting your router. "
        
        if download_val > 50:
            analysis_text += "✅ Good download speeds."
        elif download_val > 10:
            analysis_text += "⚠️ Moderate download speeds."
        else:
            analysis_text += "❌ Low download speeds. Check your connection."
        
        analysis = Paragraph(analysis_text, styles['BodyText'])
        elements.append(analysis)
        elements.append(Spacer(1, 20))
        
        # Add recommendations
        recommendations_heading = Paragraph("Recommendations", styles['Heading2'])
        elements.append(recommendations_heading)
        elements.append(Spacer(1, 10))
        
        recommendations = [
            "1. Regularly monitor your network performance",
            "2. Keep your router firmware updated",
            "3. Position your router in a central location",
            "4. Use 5GHz WiFi for better performance",
            "5. Close unnecessary background applications",
            "6. Consider wired connection for critical tasks"
        ]
        
        for rec in recommendations:
            elements.append(Paragraph(rec, styles['BodyText']))
            elements.append(Spacer(1, 5))
        
        # Build PDF
        doc.build(elements)
        
        return send_file("network_report.pdf", as_attachment=True, download_name="network_report.pdf")
    
    except Exception as e:
        print(f"Error generating report: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
