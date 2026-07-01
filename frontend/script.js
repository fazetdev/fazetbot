console.log("Script Loaded - V1.1 Production");

async function sendMessage() {
    console.log("Button Clicked");

    const input = document.getElementById("message");
    const sendBtn = document.getElementById("send-btn");
    const message = input.value.trim();

    if (!message) return;

    // Append the user's message to the chat layout using the design system
    appendMessage("user", message);
    input.value = "";

    // Throttling: Disable input and button to protect server limits
    input.disabled = true;
    sendBtn.disabled = true;

    try {
        // FIXED: Hardcoding the absolute URL ensures it speaks directly to your FastAPI backend on Port 5000
        const response = await fetch("http://127.0.0.1:5000/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        // Handles bad HTTP statuses explicitly before trying to parse JSON
        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();
        console.log(data);

        // FIXED: Changed from data.answer to data.response to read the FastAPI payload correctly
        if (data.response) {
            appendMessage("ai", data.response);
        } else {
            appendMessage("ai", "Error: Received empty response from assistant.");
        }

    } catch (error) {
        console.error(error);
        appendMessage(
            "ai",
            "Error: Cannot connect to server. Please check terminal logs."
        );
    } finally {
        // Re-enable inputs once processing finishes
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

// Builds the structured card nodes for user and AI streams
function appendMessage(sender, text) {
    const chatBox = document.getElementById("chat-box");
    
    if (sender === "user") {
        // User Card Generation
        const userDiv = document.createElement("div");
        userDiv.classList.add("user-message-card");
        userDiv.innerText = text;
        chatBox.appendChild(userDiv);
    } else {
        // AI Structured Card Generation to match index.html styling
        const aiCard = document.createElement("div");
        aiCard.classList.add("ai-message-card");

        const aiName = document.createElement("div");
        aiName.classList.add("ai-name");
        aiName.innerText = "Fazet AI";

        const aiBody = document.createElement("div");
        aiBody.classList.add("ai-body");

        // Isolated template strings to prevent tag loss during text copy/pasting
        let boldTemplate = '<strong>$1</strong>';
        let breakTemplate = '<br>';

        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, boldTemplate) // Formats Gemini's **bold** output
            .replace(/\n/g, breakTemplate);         // Formats standard line breaks

        aiBody.innerHTML = formattedText; 

        aiCard.appendChild(aiName);
        aiCard.appendChild(aiBody);
        chatBox.appendChild(aiCard);
    }

    // Auto-scroll screen down comfortably
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Action Events Integration
document
    .getElementById("send-btn")
    .addEventListener("click", sendMessage);

document
    .getElementById("message")
    .addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey && !this.disabled) {
            e.preventDefault();
            sendMessage();
        }
    });