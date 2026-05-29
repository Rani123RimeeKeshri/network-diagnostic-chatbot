# 🤖 Network Diagnostic Chatbot

An AI-powered network diagnostic chatbot with real-time network monitoring, dark/light theme support, and professional UI.

## ✨ Features

✅ **AI-Powered Responses** - Real conversational AI using Gemini or OpenRouter APIs  
✅ **Dark/Light Theme Toggle** - Professional theme switching with localStorage persistence  
✅ **📖 README Modal** - On/off help guide with setup instructions  
✅ **Real-time Network Monitoring** - Live dashboard with:
  - Download/Upload speeds
  - Network latency (Ping)
  - IP address
  - Connection status

✅ **Network Analytics** - Chart.js visualization of network metrics  
✅ **Voice Input** - 🎤 Speak your issue (Web Speech API)  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **Troubleshooting Solutions** - Expert guidance for:
  - WiFi connectivity issues
  - DNS problems
  - Router configuration
  - Network diagnostics
  - Speed optimization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rani123RimeeKeshri/network-diagnostic-chatbot.git
   cd network-diagnostic-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file with API keys**
   ```bash
   cp .env.example .env
   ```

4. **Add your API keys to `.env`**
   
   **For Google Gemini:**
   - Visit: https://ai.google.dev/tutorials/setup
   - Get your free API key
   - Add to `.env`: `GEMINI_API_KEY=your_key_here`
   
   **For OpenRouter (Optional):**
   - Visit: https://openrouter.ai
   - Sign up and get API key
   - Add to `.env`: `OPENROUTER_API_KEY=your_key_here`

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 📖 How to Use

### Dashboard
- **Status** - Current connection status
- **Download** - Download speed in Mbps
- **Upload** - Upload speed in Mbps
- **Ping** - Network latency in milliseconds
- **IP Address** - Your current public IP

### Chat
1. Type your network issue in the input field
2. Press **Enter** or click **➤** button
3. Or use **🎤** for voice input
4. Get AI-powered solutions instantly

### Theme Toggle
- Click **🌙** button in top-right to switch themes
- Your preference is saved automatically

### Help
- Click **📖** button to view guide and setup instructions

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# AI API Keys
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key

# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=True
```

### Switching AI Provider

Edit `static/script.js` line 106:

```javascript
ai_type: "gemini"  // or "openrouter"
```

---

## 📁 Project Structure

```
network-diagnostic-chatbot/
├── app.py                    # Flask backend with AI integration
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── templates/
│   └── index.html           # Main UI with README modal
└── static/
    ├── style.css            # Dark/Light theme styles
    └── script.js            # Frontend logic & theme toggle
```

---

## 🎨 Theme System

The app uses CSS variables for easy theme management:

**Light Mode (Default):**
- Purple gradient background
- Light containers
- White chat messages

**Dark Mode:**
- Deep blue-black gradient
- Dark containers
- Dark chat backgrounds

Toggle saved in browser's localStorage.

---

## 🤖 AI Integration

### Google Gemini API
- Free tier available
- Up to 60 requests per minute
- Excellent for conversational AI
- **Setup:** https://ai.google.dev/tutorials/setup

### OpenRouter API
- Access to multiple AI models
- Automatic model routing
- Flexible pricing
- **Setup:** https://openrouter.ai

---

## 🔍 Common Network Issues Handled

| Issue | Solution Category |
|-------|------------------|
| WiFi not connecting | Connectivity troubleshooting |
| Slow internet | Speed optimization |
| High ping | Latency reduction |
| DNS issues | DNS configuration |
| Router problems | Hardware diagnostics |
| Packet loss | Network stability |
| IP address issues | Network configuration |

---

## 📊 Technology Stack

**Backend:**
- Flask - Web framework
- Python 3.8+
- Gemini API / OpenRouter API

**Frontend:**
- HTML5
- CSS3 (with CSS Variables)
- JavaScript (ES6+)
- Chart.js - Network visualization
- Web Speech API - Voice input

**Libraries:**
- speedtest-cli - Speed testing
- psutil - System information
- reportlab - PDF generation
- requests - HTTP client

---

## 🐛 Troubleshooting

### API Key Not Working
- Verify key is correctly copied to `.env`
- Check API quota limits
- Ensure internet connection

### Voice Input Not Working
- Only works in Chromium-based browsers (Chrome, Edge, Brave)
- Requires HTTPS in production
- Check microphone permissions

### Dashboard Shows "-- Mbps"
- Server is still loading network info
- Check Flask console for errors
- Ensure network access

---

## 📝 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/` | GET | Serve main UI |
| `/get` | POST | Send message to AI |
| `/network` | GET | Get network metrics |
| `/report` | GET | Generate PDF report |

---

## 🚀 Deployment

### Local Production
```bash
FLASK_ENV=production python app.py
```

### Cloud Deployment (Heroku)
```bash
heroku create your-app-name
git push heroku main
heroku config:set GEMINI_API_KEY=your_key
```

---

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 👨‍💻 Author

**Rani123RimeeKeshri**

- GitHub: [@Rani123RimeeKeshri](https://github.com/Rani123RimeeKeshri)
- Project: [network-diagnostic-chatbot](https://github.com/Rani123RimeeKeshri/network-diagnostic-chatbot)

---

## 🙏 Support

If you find this helpful, please:
- ⭐ Star the repository
- 🐛 Report bugs via GitHub Issues
- 💡 Suggest improvements
- 📢 Share with others

---

## 📞 Contact & Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: Check GitHub profile

---

**Happy Network Diagnosing! 🎉**