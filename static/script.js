function addMessage(sender, text, source = "", path = "") {
  let chat = document.getElementById("chatbox");
  let msg = document.createElement("div");
  msg.className = "message";

  if (sender === "user") {
    msg.innerHTML = "<b class='user'>You:</b> " + text;
  } else {
    msg.innerHTML = "<b class='bot'>AskGmu:</b> " + text;

    if (source) {
      msg.innerHTML +=
        "<div class='source'>Source: " + source +
        (path ? " — <a href='" + path + "' target='_blank'>Open PDF</a>" : "") +
        "</div>";
    }
  }

  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
  let input = document.getElementById("userInput");
  let message = input.value.trim();

  if (!message) return;

  addMessage("user", message);
  input.value = "";
  input.disabled = true;

  fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message: message })
  })
    .then(res => res.json())
    .then(data => {
      addMessage("bot", data.answer, data.source, data.path);
      input.disabled = false;
    })
    .catch(() => {
      addMessage("bot", "Error: Server not responding");
      input.disabled = false;
    });
}

function refreshData() {
  addMessage("bot", "Refreshing data... please wait");

  fetch("/refresh")
    .then(res => res.json())
    .then(data => {
      addMessage("bot", data.message);
    })
    .catch(() => {
      addMessage("bot", "Error refreshing data");
    });
}

document.getElementById("userInput").addEventListener("keydown", function(e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});