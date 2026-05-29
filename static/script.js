// Theme Toggle
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    
    // Save preference
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
        document.querySelector('.theme-btn').textContent = '☀️';
    } else {
        localStorage.setItem('theme', 'light');
        document.querySelector('.theme-btn').textContent = '🌙';
    }
}

// README Toggle
function toggleReadme() {
    const modal = document.getElementById('readme-modal');
    modal.classList.toggle('show');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('readme-modal');
    if (event.target == modal) {
        modal.classList.remove('show');
    }
}

// Load theme on startup
window.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.querySelector('.theme-btn').textContent = '☀️';
    }
});

function getTime(){
    let now = new Date();
    return now.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function sendMessage(){
    let inputField = document.getElementById("user-input");
    let message = inputField.value;

    if(message.trim() === ""){
        return;
    }

    let chatBox = document.getElementById("chat-box");

    // USER MESSAGE
    chatBox.innerHTML += `
        <div class="user-message">
            <b>You:</b> ${message}
            <div class="timestamp">${getTime()}</div>
        </div>
    `;

    inputField.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // TYPING ANIMATION
    chatBox.innerHTML += `
        <div class="typing" id="typing">
            🤖 Bot is typing...
        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;

    // FETCH RESPONSE
    try {
        const response = await fetch("/get", {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                message:message,
                ai_type: "gemini" // or "openrouter"
            })
        });

        const data = await response.json();

        // REMOVE TYPING
        document.getElementById("typing").remove();

        // BOT MESSAGE
        chatBox.innerHTML += `
            <div class="bot-message">
                <b>Bot:</b> ${data.reply}
                <div class="timestamp">${getTime()}</div>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;
    } catch(error) {
        console.error("Error:", error);
        document.getElementById("typing").remove();
        chatBox.innerHTML += `
            <div class="bot-message">
                <b>Bot:</b> Sorry, I encountered an error. Please try again.
                <div class="timestamp">${getTime()}</div>
            </div>
        `;
    }
}

// ENTER KEY
document.getElementById("user-input")
.addEventListener("keypress", function(event){
    if(event.key === "Enter"){
        sendMessage();
    }
});

// VOICE INPUT
function startVoice(){
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";

    recognition.onresult = function(event){
        document.getElementById("user-input").value =
        event.results[0][0].transcript;
        sendMessage();
    };

    recognition.start();
}

async function loadNetworkInfo(){
    try{
        const response = await fetch("/network");
        const data = await response.json();

        document.getElementById("status").innerText =
        data.status;

        document.getElementById("download").innerText =
        data.download + " Mbps";

        document.getElementById("upload").innerText =
        data.upload + " Mbps";

        document.getElementById("ping").innerText =
        data.ping + " ms";

        document.getElementById("ip").innerText =
        data.ip;

        updateGraph(data.download, data.upload);

    }catch(error){
        console.log(error);
    }
}

const ctx = document.getElementById('networkChart');

const networkChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Download Mbps',
                data: [],
                borderColor: '#00ffcc',
                tension: 0.4
            },
            {
                label: 'Upload Mbps',
                data: [],
                borderColor: '#ffcc00',
                tension: 0.4
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// UPDATE GRAPH
function updateGraph(download, upload){
    const time = new Date().toLocaleTimeString();

    networkChart.data.labels.push(time);
    networkChart.data.datasets[0].data.push(download);
    networkChart.data.datasets[1].data.push(upload);

    // Keep only latest 10 entries
    if(networkChart.data.labels.length > 10){
        networkChart.data.labels.shift();
        networkChart.data.datasets[0].data.shift();
        networkChart.data.datasets[1].data.shift();
    }

    networkChart.update();
}

window.onload = function(){
    loadNetworkInfo();
    setInterval(loadNetworkInfo, 5000);
};