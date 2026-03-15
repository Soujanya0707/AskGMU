function addMessage(sender, text, source = "") {
  let chat = document.getElementById("chatbox");
  let msg = document.createElement("div");
  msg.className = "message";

  if (sender === "user") {
    msg.innerHTML = "<b class='user'>You:</b> " + text;
  } else {
    msg.innerHTML = "<b class='bot'>Bot:</b> " + text;
    if (source != "") {
      msg.innerHTML += "<div class='source'>Source: " + source + "</div>";
    }
  }

  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
  let input = document.getElementById("userInput");
  let message = input.value;

  if (message === "") return;

  addMessage("user", message);
  input.value = "";

  fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message: message })
  })
    .then(res => res.json())
    .then(data => {
      addMessage("bot", data.answer, data.source);
    });
}

function refreshData() {
  addMessage("bot", "Refreshing data... please wait");

  fetch("/refresh")
    .then(res => res.json())
    .then(data => {
      addMessage("bot", data.message);
    });
}
