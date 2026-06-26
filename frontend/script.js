Console.log("Script Loaded");

Async function sendMessage() {
    Console.log("Button Clicked");

    Const input = document.getElementById("message");
    Const sendBtn = document.getElementById("send-btn");
    Const message = input.value.trim();

    If (!message) return;

    // Append the user's message to the chat layout using the new design system
    AppendMessage("user", message);
    Input.value = "";

    // Throttling: Disable input and button to protect server limits
    Input.disabled = true;
    SendBtn.disabled = true;

    Try {
        Const response = await fetch("/api/chat", {
            Method: "POST",
            Headers: {
                "Content-Type": "application/json"
            },
            Body: JSON.stringify({
                Message: message
            })
        });

        Const data = await response.json();
        Console.log(data);

        If (data.answer) {
            AppendMessage("ai", data.answer);
        } else {
            AppendMessage("ai", "Error: Received empty response from assistant.");
        }

    } catch (error) {
        Console.error(error);
        AppendMessage(
            "ai",
            "Error: Cannot connect to server"
        );
    } finally {
        // Re-enable inputs once processing finishes
        Input.disabled = false;
        SendBtn.disabled = false;
        Input.focus();
    }
}

// Updated to build the beautiful new structured card nodes
function appendMessage(sender, text) {
    Const chatBox = document.getElementById("chat-box");
    
    If (sender === "user") {
        // User Card Generation
        Const userDiv = document.createElement("div");
        UserDiv.classList.add("user-message-card");
        UserDiv.innerText = text;
        ChatBox.appendChild(userDiv);
    } else {
        // AI Structured Card Generation to match index.html styling
        Const aiCard = document.createElement("div");
        AiCard.classList.add("ai-message-card");

        Const aiName = document.createElement("div");
        AiName.classList.add("ai-name");
        AiName.innerText = "Fazet AI";

        Const aiBody = document.createElement("div");
        AiBody.classList.add("ai-body");
        AiBody.innerText = text;

        AiCard.appendChild(aiName);
        AiCard.appendChild(aiBody);
        ChatBox.appendChild(aiCard);
    }

    // Auto-scroll screen down comfortably
    ChatBox.scrollTop = chatBox.scrollHeight;
}

document
    .getElementById("send-btn")
    .addEventListener("click", sendMessage);

// Clear form interceptor matching desktop textarea rules
document
    .getElementById("message")
    .addEventListener("keydown", function (e) {
        If (e.key === "Enter" && !e.shiftKey && !this.disabled) {
            E.preventDefault();
            SendMessage();
        }
    });
