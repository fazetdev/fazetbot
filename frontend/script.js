async function sendMessage() {

    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (!message) return;

    appendMessage("user", message);

    input.value = "";

    try {

        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        appendMessage("ai", data.answer);

    } catch (error) {

        appendMessage("ai", "Error: Cannot connect to server");

        console.error(error);
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