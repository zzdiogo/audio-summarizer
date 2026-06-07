const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const fileSelected = document.getElementById("file-selected");
const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");
const btnClear = document.getElementById("btn-clear");
const btnSummarize = document.getElementById("btn-summarize");
const languageSelect = document.getElementById("language");

const uploadSection = document.getElementById("upload-section");
const loadingSection = document.getElementById("loading-section");
const errorSection = document.getElementById("error-section");
const resultsSection = document.getElementById("results-section");
const loadingStep = document.getElementById("loading-step");
const errorMessage = document.getElementById("error-message");

let selectedFile = null;
let loadingTimer = null;

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function setFile(file) {
  selectedFile = file;
  fileName.textContent = file.name;
  fileSize.textContent = formatSize(file.size);
  fileSelected.classList.remove("hidden");
  dropzone.classList.add("hidden");
  btnSummarize.disabled = false;
}

function clearFile() {
  selectedFile = null;
  fileInput.value = "";
  fileSelected.classList.add("hidden");
  dropzone.classList.remove("hidden");
  btnSummarize.disabled = true;
}

function showSection(section) {
  [uploadSection, loadingSection, errorSection, resultsSection].forEach((el) => {
    el.classList.add("hidden");
  });
  section.classList.remove("hidden");
}

function fillList(elementId, items) {
  const list = document.getElementById(elementId);
  list.innerHTML = "";
  if (!items || items.length === 0) {
    list.classList.add("empty-list");
    return;
  }
  list.classList.remove("empty-list");
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
}

function showResults(data) {
  const duration = data.duration_seconds
    ? `${Math.floor(data.duration_seconds / 60)} min ${Math.round(data.duration_seconds % 60)} s`
    : null;

  document.getElementById("meta-duration").textContent = duration
    ? `⏱ ${duration}`
    : "";
  document.getElementById("meta-language").textContent = data.language
    ? `🌐 ${data.language.toUpperCase()}`
    : "";

  document.getElementById("overview-text").textContent = data.summary.overview;
  fillList("list-topics", data.summary.main_topics);
  fillList("list-points", data.summary.key_points);
  fillList("list-takeaways", data.summary.takeaways);
  document.getElementById("transcription-text").textContent = data.transcription;

  showSection(resultsSection);
}

function parseError(response, body) {
  if (typeof body === "string") return body;
  if (body.detail) {
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((e) => e.msg || JSON.stringify(e)).join("; ");
    }
  }
  return `Error ${response.status}: invalid request.`;
}

async function summarize() {
  if (!selectedFile) return;

  showSection(loadingSection);
  const steps = [
    "Transcribing audio with Whisper...",
    "Analyzing content...",
    "Generating summary with LLM...",
  ];
  let step = 0;
  loadingStep.textContent = steps[0];
  loadingTimer = setInterval(() => {
    step = (step + 1) % steps.length;
    loadingStep.textContent = steps[step];
  }, 10000);

  const formData = new FormData();
  formData.append("audio", selectedFile);
  const lang = languageSelect.value;
  if (lang) formData.append("language", lang);

  try {
    const response = await fetch("/api/v1/summarize", {
      method: "POST",
      body: formData,
    });

    const body = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(parseError(response, body));
    }

    showResults(body);
  } catch (err) {
    errorMessage.textContent = err.message || "Unknown error.";
    showSection(errorSection);
  } finally {
    clearInterval(loadingTimer);
  }
}

dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) setFile(file);
});

btnClear.addEventListener("click", clearFile);
btnSummarize.addEventListener("click", summarize);
document.getElementById("btn-retry").addEventListener("click", () => showSection(uploadSection));
document.getElementById("btn-new").addEventListener("click", () => {
  clearFile();
  showSection(uploadSection);
});
