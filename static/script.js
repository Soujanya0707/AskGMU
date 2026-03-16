function addMessage(sender, text, source = "", path = "") {
  let chat = document.getElementById("chatbox");
  let msg = document.createElement("div");
  msg.className = "message";

  if (sender === "user") {
    msg.innerHTML = "<b class='user'>You:</b> " + text;
  } else {
    msg.innerHTML = "<b class='bot'>AskGmu:</b> " + text;
    if (source != "") {
      msg.innerHTML += "<div class='source'>Source: " + source + 
      " — <a href='file:///" + path.replace(/\\/g, "/") + "' target='_blank'>Open File</a></div>";
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
      addMessage("bot", data.answer, data.source, data.path);
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