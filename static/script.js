// ==================== THEME MANAGEMENT ====================
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const themeBtn = document.querySelector('.theme-btn');
    
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
        themeBtn.textContent = '☀️';
    } else {
        localStorage.setItem('theme', 'light');
        themeBtn.textContent = '🌙';
    }
}

// Load saved theme on startup
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.querySelector('.theme-btn').textContent = '☀️';
    }
});

// ==================== MODAL MANAGEMENT ====================
function toggleReadme() {
    const modal = document.getElementById('readme-modal');
    modal.classList.toggle('show');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('readme-modal');
    if (event.target === modal) {
        modal.classList.remove('show');
    }
}

// ==================== CHAT FUNCTIONALITY ====================
function getTime() {
    let now = new Date();
    return now.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

async function sendMessage() {
    let inputField = document.getElementById("user-input");
    let message = inputField.value.trim();

    if (!message) {
        alert("Please enter a message!");
        return;
    }

    let chatBox = document.getElementById("chat-box");

    // Add user message
    chatBox.innerHTML += `
        <div class="user-message">
            <b>You:</b> ${escapeHtml(message)}
            <div class="timestamp">${getTime()}</div>
        </div>
    `;

    inputField.value = "";
    inputField.focus();
    chatBox.scrollTop = chatBox.scrollHeight;

    // Show typing animation
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing';
    typingDiv.className = 'typing';
    typingDiv.innerHTML = '🤖 Bot is typing...';
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("/get", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                ai_type: "gemini"
            })
        });

        const data = await response.json();
        
        // Remove typing indicator
        const typing = document.getElementById("typing");
        if (typing) typing.remove();

        // Add bot message
        const botMessage = data.reply || "Sorry, I couldn't process your request.";
        chatBox.innerHTML += `
            <div class="bot-message">
                <b>Bot:</b> ${escapeHtml(botMessage)}
                <div class="timestamp">${getTime()}</div>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        console.error("Error:", error);
        
        const typing = document.getElementById("typing");
        if (typing) typing.remove();
        
        chatBox.innerHTML += `
            <div class="bot-message">
                <b>Bot:</b> ❌ Sorry, I encountered an error. Please check your API key and try again.
                <div class="timestamp">${getTime()}</div>
            </div>
        `;
        
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// Send message on Enter key
document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById("user-input");
    if (userInput) {
        userInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                sendMessage();
            }
        });
    }
});

// ==================== VOICE INPUT ====================
function startVoice() {
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        alert("Your browser doesn't support voice input. Try Chrome, Edge, or Safari.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = true;

    const micBtn = document.querySelector('.mic-btn');
    micBtn.textContent = '🎤 ...';
    micBtn.disabled = true;

    recognition.onstart = function() {
        console.log("Listening...");
    };

    recognition.onresult = function(event) {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                document.getElementById("user-input").value = transcript;
            } else {
                interimTranscript += transcript;
            }
        }
    };

    recognition.onend = function() {
        micBtn.textContent = '🎤';
        micBtn.disabled = false;
        const message = document.getElementById("user-input").value.trim();
        if (message) {
            sendMessage();
        }
    };

    recognition.onerror = function(event) {
        console.error("Voice recognition error:", event.error);
        micBtn.textContent = '🎤';
        micBtn.disabled = false;
        alert("Error: " + event.error);
    };

    recognition.start();
}

// ==================== NETWORK MONITORING ====================
let networkChart = null;

async function loadNetworkInfo() {
    try {
        const response = await fetch("/network");
        const data = await response.json();

        // Update dashboard
        document.getElementById("status").textContent = data.status === "Connected" ? "✅ Connected" : "❌ Disconnected";
        document.getElementById("download").textContent = data.download + " Mbps";
        document.getElementById("upload").textContent = data.upload + " Mbps";
        
        const pingColor = data.ping < 50 ? "🟢" : data.ping < 100 ? "🟡" : "🔴";
        document.getElementById("ping").textContent = pingColor + " " + data.ping + " ms";
        
        document.getElementById("ip").textContent = data.ip;

        // Update chart
        updateGraph(data.download, data.upload);

    } catch (error) {
        console.error("Error loading network info:", error);
        document.getElementById("status").textContent = "❌ Error";
    }
}

function updateGraph(download, upload) {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (!networkChart) {
        initChart();
    }

    networkChart.data.labels.push(time);
    networkChart.data.datasets[0].data.push(download);
    networkChart.data.datasets[1].data.push(upload);

    // Keep only last 10 entries for performance
    if (networkChart.data.labels.length > 10) {
        networkChart.data.labels.shift();
        networkChart.data.datasets[0].data.shift();
        networkChart.data.datasets[1].data.shift();
    }

    networkChart.update();
}

function initChart() {
    const ctx = document.getElementById('networkChart');
    if (!ctx) return;

    networkChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Download (Mbps)',
                    data: [],
                    borderColor: '#00ffcc',
                    backgroundColor: 'rgba(0, 255, 204, 0.1)',
                    tension: 0.4,
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'Upload (Mbps)',
                    data: [],
                    borderColor: '#ffcc00',
                    backgroundColor: 'rgba(255, 204, 0, 0.1)',
                    tension: 0.4,
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: { size: 10 }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.6)',
                        font: { size: 9 }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.6)',
                        font: { size: 9 }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

// ==================== EXPORT REPORT ====================
function exportReport() {
    try {
        // Create a simple text report
        const status = document.getElementById("status").textContent;
        const download = document.getElementById("download").textContent;
        const upload = document.getElementById("upload").textContent;
        const ping = document.getElementById("ping").textContent;
        const ip = document.getElementById("ip").textContent;
        
        const reportText = `
NETWORK DIAGNOSTIC REPORT
Generated: ${new Date().toLocaleString()}

=== NETWORK STATISTICS ===
Status: ${status}
Download Speed: ${download}
Upload Speed: ${upload}
Ping: ${ping}
IP Address: ${ip}

=== ANALYSIS ===
Your current network performance has been captured above.
For detailed PDF report, please visit /report endpoint.

=== RECOMMENDATIONS ===
1. Monitor your network regularly
2. Keep router firmware updated
3. Position router in central location
4. Use 5GHz WiFi for better speeds
5. Close unnecessary background apps

Report generated by Network Diagnostic Chatbot
`;

        // Create blob and download
        const blob = new Blob([reportText], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `network_report_${new Date().getTime()}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        alert("✅ Report downloaded successfully!");

    } catch (error) {
        console.error("Error exporting report:", error);
        alert("❌ Error exporting report. Please try again.");
    }
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize chart
    initChart();
    
    // Load initial network info
    loadNetworkInfo();
    
    // Update network info every 5 seconds
    setInterval(loadNetworkInfo, 5000);
    
    console.log("✅ Network Diagnostic Chatbot initialized successfully!");
});
