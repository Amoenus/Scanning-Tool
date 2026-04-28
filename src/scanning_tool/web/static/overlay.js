const STORAGE_KEY = "overlay-selected-region";
const DEFAULT_REGION = "STANTON";
const POLL_INTERVAL_MS = 1000;

const state = {
  region: DEFAULT_REGION,
  timerId: 0,
  wakeLock: null,
  installPromptEvent: null,
};

const elements = {
  name: null,
  code: null,
  raw: null,
  minerals: null,
  statusMessage: null,
  updatedAt: null,
  regionInputs: [],
  fullscreenToggle: null,
  installButton: null,
};

globalThis.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  state.installPromptEvent = event;
  if (elements.installButton) {
    showInstallButton();
  }
});

globalThis.addEventListener("appinstalled", () => {
  setStatus("Overlay installed as an app.", "success");
  hideInstallButton();
});

function getElement(id) {
  const element = document.getElementById(id);
  if (!element) {
    throw new Error(`Missing required element: ${id}`);
  }
  return element;
}

function initElements() {
  elements.name = getElement("name");
  elements.code = getElement("code");
  elements.category = getElement("category");
  elements.raw = getElement("raw");
  elements.minerals = getElement("minerals");
  elements.statusMessage = getElement("status-message");
  elements.updatedAt = getElement("updated-at");
  elements.fullscreenToggle = document.getElementById("fullscreen-toggle");
  elements.installButton = document.getElementById("install-pwa");
  elements.regionInputs = Array.from(document.querySelectorAll('input[name="region"]'));
}

function initRegionSelection() {
  const savedRegion = localStorage.getItem(STORAGE_KEY);
  state.region = savedRegion || DEFAULT_REGION;

  elements.regionInputs.forEach((input) => {
    input.checked = input.value === state.region;
    input.addEventListener("change", onRegionChange);
  });
}

function initFullscreenButton() {
  if (!elements.fullscreenToggle) {
    return;
  }

  elements.fullscreenToggle.addEventListener("click", onFullscreenToggle);
  document.addEventListener("fullscreenchange", setFullscreenButtonState);
  document.addEventListener("visibilitychange", async () => {
    if (document.visibilityState === "visible" && document.fullscreenElement) {
      await requestWakeLock();
    }
  });

  if (elements.installButton) {
    elements.installButton.addEventListener("click", onInstallClick);
  }

  setFullscreenButtonState();

  if (state.installPromptEvent) {
    showInstallButton();
  } else {
    hideInstallButton();
  }
}

async function onFullscreenToggle() {
  if (document.fullscreenElement) {
    await exitFullscreenMode();
  } else {
    await enterFullscreenMode();
  }
}

async function enterFullscreenMode() {
  try {
    if (document.documentElement.requestFullscreen) {
      await document.documentElement.requestFullscreen();
    }

    await requestWakeLock();
  } catch (error) {
    console.warn("Fullscreen or wake lock request failed:", error);
  }
}

async function exitFullscreenMode() {
  try {
    if (document.exitFullscreen && document.fullscreenElement) {
      await document.exitFullscreen();
    }
  } catch (error) {
    console.warn("Exit fullscreen failed:", error);
  } finally {
    await releaseWakeLock();
  }
}

function setFullscreenButtonState() {
  if (!elements.fullscreenToggle) {
    return;
  }

  if (document.fullscreenElement) {
    elements.fullscreenToggle.textContent = "Exit fullscreen";
  } else {
    elements.fullscreenToggle.textContent = "Fullscreen";
  }
}

function onBeforeInstallPrompt(event) {
  event.preventDefault();
  state.installPromptEvent = event;
  showInstallButton();
}

async function onInstallClick() {
  if (!state.installPromptEvent) {
    return;
  }

  state.installPromptEvent.prompt();
  const choice = await state.installPromptEvent.userChoice;

  if (choice.outcome === "accepted") {
    setStatus("Install accepted. The app may now be added to your home screen.", "success");
  } else {
    setStatus("Install dismissed.", "warning");
  }

  state.installPromptEvent = null;
  hideInstallButton();
}

function onAppInstalled() {
  setStatus("Overlay installed as an app.", "success");
  hideInstallButton();
}

function showInstallButton() {
  if (elements.installButton) {
    elements.installButton.classList.remove("hidden");
  }
}

function hideInstallButton() {
  if (elements.installButton) {
    elements.installButton.classList.add("hidden");
  }
}

async function requestWakeLock() {
  if (!("wakeLock" in navigator)) {
    return;
  }

  try {
    state.wakeLock = await navigator.wakeLock.request("screen");
    state.wakeLock.addEventListener("release", () => {
      state.wakeLock = null;
    });
  } catch (error) {
    console.warn("Wake lock request failed:", error);
  }
}

async function releaseWakeLock() {
  if (!state.wakeLock) {
    return;
  }

  try {
    await state.wakeLock.release();
  } catch (error) {
    console.warn("Wake lock release failed:", error);
  } finally {
    state.wakeLock = null;
  }
}

function onRegionChange(event) {
  state.region = event.target.value;
  localStorage.setItem(STORAGE_KEY, state.region);
  schedulePoll(0);
}

function isCompactLayout() {
  return globalThis.matchMedia("(max-width: 520px)").matches;
}

function setStatus(text, type = "info") {
  elements.statusMessage.textContent = text;
  elements.statusMessage.className = "hud-status";
  if (type) {
    elements.statusMessage.classList.add(`hud-status--${type}`);
  }
}

function formatUpdatedAt(timestamp) {
  if (!timestamp) {
    return "";
  }

  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderUpdatedAt(timestamp) {
  const formatted = formatUpdatedAt(timestamp);
  elements.updatedAt.textContent = formatted ? `Updated ${formatted}` : "";
}

function renderCardList(data) {
  const cards = data
    .map(
      (row) => `
      <div class="rounded-3xl border border-sky-400/10 bg-slate-900/70 p-4 shadow-sm shadow-sky-500/10">
        <div class="flex items-center justify-between gap-3">
          <p class="font-semibold uppercase tracking-[0.2em] text-slate-100" style="color:${row.color};">${row.name}</p>
          <span class="rounded-full bg-slate-800/80 px-3 py-1 text-[11px] uppercase tracking-[0.24em] text-slate-300">${row.prob}</span>
        </div>
        <div class="mt-3 grid grid-cols-2 gap-3 text-[11px] uppercase tracking-[0.24em] text-slate-300">
          <div class="rounded-2xl bg-slate-950/70 p-3">
            <p class="text-[10px] text-slate-400">Min</p>
            <p class="mt-1 font-semibold text-slate-100">${row.min}</p>
          </div>
          <div class="rounded-2xl bg-slate-950/70 p-3">
            <p class="text-[10px] text-slate-400">Max</p>
            <p class="mt-1 font-semibold text-slate-100">${row.max}</p>
          </div>
          <div class="col-span-2 rounded-2xl bg-slate-950/70 p-3">
            <p class="text-[10px] text-slate-400">Median</p>
            <p class="mt-1 font-semibold text-slate-100">${row.med}</p>
          </div>
        </div>
      </div>`,
    )
    .join("");

  elements.minerals.innerHTML = `<div class="space-y-3">${cards}</div>`;
}

function renderTable(data) {
  if (isCompactLayout()) {
    renderCardList(data);
    return;
  }

  const rows = data
    .map(
      (row) => `
      <tr>
        <td style="color:${row.color}; font-weight:bold;">${row.name}</td>
        <td>${row.prob}</td>
        <td>${row.min}</td>
        <td>${row.max}</td>
        <td>${row.med}</td>
      </tr>`,
    )
    .join("");

  elements.minerals.innerHTML = `
    <table>
      <tr><th>Mineral</th><th>Prob</th><th>Min</th><th>Max</th><th>Med</th></tr>
      ${rows}
    </table>`;
}

function showEmptyState(category) {
  const message = category && category.toLowerCase().includes("salvage")
    ? "No mineral composition available for salvage targets."
    : "No deposit table is available for this scan.";

  elements.minerals.innerHTML = `<div class="hud-empty">${message}</div>`;
}

function renderPayload(payload) {
  if (payload.status === "no_scan") {
    setStatus("Waiting for the next scan result…", "warning");
    elements.name.textContent = "No scan available";
    elements.code.textContent = "";
    elements.category.textContent = "";
    elements.raw.textContent = "";
    elements.minerals.innerHTML = "";
    renderUpdatedAt(payload.updated_at);
    return;
  }

  if (payload.status === "invalid_scan") {
    setStatus("OCR detected a code, but no deposit metadata was found.", "warning");
    elements.name.textContent = "Invalid scan result";
    elements.code.textContent = payload.code_raw ? `Code: ${payload.code_raw}` : "";
    elements.category.textContent = "";
    elements.raw.textContent = "";
    elements.minerals.innerHTML = "";
    renderUpdatedAt(payload.updated_at);
    return;
  }

  const title = payload.info.name || "Unknown deposit";
  elements.name.textContent = payload.info.deposits
    ? `${title} x${payload.info.deposits}`
    : title;
  elements.code.textContent = `Code: ${payload.code ?? ""}`;
  elements.category.textContent = payload.info.category
    ? payload.info.category.toUpperCase()
    : "";
  elements.raw.textContent = payload.code_raw
    ? `(raw: ${payload.code_raw})`
    : "";

  if (Array.isArray(payload.table) && payload.table.length) {
    renderTable(payload.table);
  } else {
    showEmptyState(payload.info.category || "");
  }

  setStatus("Overlay synchronized with latest scan.", "success");
  renderUpdatedAt(payload.updated_at);
}

async function poll() {
  setStatus("Updating overlay…", "loading");
  try {
    const response = await fetch(
      `/status?region=${encodeURIComponent(state.region)}`,
      {
        cache: "no-store",
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    renderPayload(payload);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    setStatus(`Connection error: ${message}`, "error");
    elements.minerals.innerHTML = "";
    renderUpdatedAt("");
  } finally {
    schedulePoll(POLL_INTERVAL_MS);
  }
}

function schedulePoll(delay) {
  if (state.timerId) {
    clearTimeout(state.timerId);
  }
  state.timerId = globalThis.setTimeout(poll, delay);
}

globalThis.addEventListener("DOMContentLoaded", () => {
  initElements();
  initRegionSelection();
  initFullscreenButton();
  poll();
});
