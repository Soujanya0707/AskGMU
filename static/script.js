function addMessage(sender, text, sources = []) {
  let chat = document.getElementById("chatbox");
  let msg = document.createElement("div");
  msg.className = "message " + sender;

  msg.textContent = text;

  if (sender === "bot" && sources.length > 0) {
    let srcDiv = document.createElement("div");
    srcDiv.className = "source";
    srcDiv.innerHTML = "<b>Top matching documents:</b>";

    let ol = document.createElement("ol");
    for (let s of sources) {
      let li = document.createElement("li");

      let dateBadge = s.date
        ? `<span class="date-badge">${s.date}</span> `
        : "";

      let label = s.name || s.file;

      li.innerHTML = s.path
        ? `${dateBadge}${label} — <a href="${s.path}" target="_blank">Open PDF</a>`
        : `${dateBadge}${label}`;

      ol.appendChild(li);
    }

    srcDiv.appendChild(ol);
    msg.appendChild(srcDiv);
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
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message })
  })
    .then(res => res.json())
    .then(data => {
      addMessage("bot", data.answer, data.sources);
      input.disabled = false;
      input.focus();
    })
    .catch(() => {
      addMessage("bot", "Error: Server not responding.");
      input.disabled = false;
    });
}

function refreshData() {
  addMessage("bot", "Refreshing data, please wait...");
  fetch("/refresh")
    .then(res => res.json())
    .then(data => addMessage("bot", data.message))
    .catch(() => addMessage("bot", "Error refreshing data."));
}

document.getElementById("userInput").addEventListener("keydown", function (e) {
  if (e.key === "Enter") sendMessage();
});