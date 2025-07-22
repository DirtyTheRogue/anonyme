// logs.js POUR MIEUX AFFICHER LES LOGS 5ON VERRA PLUS TARD°
const logs = [];

export function addLog(type, message) {
  const timestamp = new Date().toLocaleString();
  const logEntry = { type, message, timestamp };
  logs.push(logEntry);
  renderLogs();
}

function renderLogs(filter = "all") {
  const logList = document.getElementById("log-list");
  if (!logList) return; // Évite les erreurs si le conteneur n'existe pas encore

  logList.innerHTML = "";
  logs
    .filter(log => filter === "all" || log.type === filter)
    .forEach(log => {
      const logItem = document.createElement("li");
      logItem.classList.add("log-item", log.type);
      logItem.innerHTML = `<span>${log.message}</span> <span class="timestamp">${log.timestamp}</span>`;
      logList.appendChild(logItem);
    });
}

export function filterLogs(type) {
  renderLogs(type);
}
