const log = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("text");
const reactor = document.getElementById("reactor");
const memList = document.getElementById("memList");
const memEmpty = document.getElementById("memEmpty");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;           // textContent keeps output safe from HTML injection
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

async function loadMemories() {
  const items = await (await fetch("/api/memories")).json();
  memList.replaceChildren();
  memEmpty.hidden = items.length > 0;
  for (const m of items) {
    const li = document.createElement("li");
    const span = document.createElement("span");
    span.textContent = "#" + m.id + " " + m.text;
    const del = document.createElement("button");
    del.textContent = "Delete";
    del.onclick = async () => {
      await fetch("/api/memories/" + m.id, { method: "DELETE" });
      loadMemories();
    };
    li.append(span, del);
    memList.appendChild(li);
  }
}

async function loadStatus() {
  const s = await (await fetch("/api/status")).json();
  document.getElementById("safeLed").classList.toggle("on", s.safe_mode);
  document.getElementById("safeText").textContent = s.safe_mode ? "Safe mode on" : "Safe mode off";
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addMessage("user", text);
  reactor.classList.add("busy");
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    addMessage("assistant", (await res.json()).reply);
  } catch (err) {
    addMessage("assistant", "I can't reach my engine. Is main.py still running?");
  }
  reactor.classList.remove("busy");
  loadMemories();
});

const micBtn = document.getElementById("mic");
let micOn = false;
micBtn.onclick = async () => {
  micOn = !micOn;
  await fetch("/api/mic", { method: "POST", body: JSON.stringify({ on: micOn }) });
};
document.getElementById("stop").onclick = () => fetch("/api/stop", { method: "POST" });
setInterval(async () => {
  const st = await (await fetch("/api/status")).json();
  micOn = st.microphone;
  document.getElementById("micLed").classList.toggle("on", micOn);
  document.getElementById("micText").textContent = st.mic_error || (micOn ? "Microphone LISTENING" : "Microphone off");
  micBtn.textContent = micOn ? "Mic: on" : "Mic: off";
  reactor.classList.toggle("busy", micOn);
  for (const a of await (await fetch("/api/alerts")).json()) {
    a.split("\n").forEach((line) => addMessage(line.startsWith("You:") ? "user" : "assistant", line.replace(/^(You|Jarvis): /, "")));
    loadMemories();
  }
}, 2000);

(async () => {
  const history = await (await fetch("/api/history")).json();
  history.forEach((m) => addMessage(m.role, m.text));
  if (!history.length) addMessage("assistant", "Good day. How can I help?");
  loadMemories();
  loadStatus();
})();
