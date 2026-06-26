console.log("Script Loaded");

async function sendMessage() {
    console.log("Button Clicked");

    const input = document.getElementById("message");
    const sendBtn = document.getElementById("send-btn");
    const message = input.value.trim();

    if (!message) return;

    // Append the user's message to the chat layout
    appendMessage("user", message);
    input.value = "";

    // Throttling: Disable input and button to protect Gemini limits
    input.disabled = true;
    sendBtn.disabled = true;

    try {
        // FIXED: Changed route path from "/chat" to "/api/chat"
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();
        console.log(data);

        // Append the AI response or an error string if returned by app.py
        if (data.answer) {
            appendMessage("ai", data.answer);
        } else {
            appendMessage("ai", "Error: Received empty response from assistant.");
        }

    } catch (error) {
        console.error(error);
        appendMessage(
            "ai",
            "Error: Cannot connect to server"
        );
    } finally {
        // Re-enable inputs once processing finishes
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus(); // Pull cursor focus back to input bar
    }
}

function appendMessage(sender, text) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);
    messageDiv.innerText = text;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

document
    .getElementById("send-btn")
    .addEventListener("click", sendMessage);

document
    .getElementById("message")
    .addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !this.disabled) {
            e.preventDefault();
            sendMessage();
        }
    });