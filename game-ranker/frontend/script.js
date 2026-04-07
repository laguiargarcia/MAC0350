let ancestryMap = {};

async function loadAncestryMap() {
  try {
    const r = await fetch("http://localhost:8000/genres/ancestry");
    ancestryMap = await r.json();
    const normalized = {};
    for (const [k, v] of Object.entries(ancestryMap)) {
      normalized[Number(k)] = v.map(Number);
    }
    ancestryMap = normalized;
  } catch (_) {
    ancestryMap = {};
  }
}
loadAncestryMap();

function checkAncestorConflict(selectEl) {
  const selected = Array.from(selectEl.selectedOptions).map(o => Number(o.value));

  for (const id of selected) {
    const ancestors = ancestryMap[id] || [];
    const conflict  = ancestors.find(a => selected.includes(a));
    if (conflict !== undefined) {
      const childName    = selectEl.querySelector(`option[value="${id}"]`)?.textContent?.trim();
      const ancestorName = selectEl.querySelector(`option[value="${conflict}"]`)?.textContent?.trim();
      return `"${childName}" já está contido em "${ancestorName}". Selecione apenas um dos dois.`;
    }
  }
  return null;
}
function loadGenreOptions() {
  const select = document.getElementById("genre-select-add");
  if (!select) return;
  fetch("http://localhost:8000/genres/options")
    .then(r => r.text())
    .then(html => { select.innerHTML = html; })
    .catch(() => {});
}

function reloadGamesTable() {
  htmx.ajax("GET", "http://localhost:8000/games", {
    target: "#games-tbody",
    swap:   "innerHTML"
  });
}

document.addEventListener("htmx:configRequest", function (evt) {
  const trigger = evt.detail.elt;
  let genreSelect = null;

  if (trigger.tagName === "FORM") {
    genreSelect = trigger.querySelector('select[name="genre_ids"][multiple]');
  }

  if (!genreSelect && trigger.hasAttribute && trigger.hasAttribute("hx-include")) {
    const includeAttr = trigger.getAttribute("hx-include");
    includeAttr.split(",").forEach(sel => {
      const el = document.querySelector(sel.trim());
      if (el && el.tagName === "SELECT" && el.name === "genre_ids" && el.multiple) {
        genreSelect = el;
      }
    });
  }

  if (!genreSelect) return;

  const error = checkAncestorConflict(genreSelect);
  if (error) {
    evt.preventDefault();
    showToast(error, "error");
  }
});

document.addEventListener("htmx:responseError", function (evt) {
  const msg = evt.detail?.xhr?.responseText || "Erro ao comunicar com o servidor.";
  let display = msg;
  try {
    const parsed = JSON.parse(msg);
    if (parsed.detail) display = parsed.detail;
  } catch (_) {}
  showToast(display, "error");
});

function showToast(message, type = "info") {
  const existing = document.querySelector(".toast");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.className = "toast toast-" + type;
  toast.textContent = message;
  document.body.appendChild(toast);

  toast.getBoundingClientRect();
  toast.classList.add("toast-visible");

  setTimeout(() => {
    toast.classList.remove("toast-visible");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

const toastStyle = document.createElement("style");
toastStyle.textContent = `
  .toast {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%) translateY(12px);
    background: #1c1c21;
    border: 1px solid #2a2a32;
    color: #e8e8ec;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    letter-spacing: .05em;
    padding: 10px 20px;
    border-radius: 6px;
    opacity: 0;
    transition: opacity .25s, transform .25s;
    z-index: 999;
    max-width: 400px;
    text-align: center;
  }
  .toast-visible {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
  .toast-error {
    border-color: #ff4d6d;
    color: #ff4d6d;
  }
`;
document.head.appendChild(toastStyle);
