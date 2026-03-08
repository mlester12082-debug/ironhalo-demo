const submitBtn = document.getElementById("submitBtn");
const configInput = document.getElementById("configInput");

const resultContainer = document.getElementById("resultContainer");
const resultOutput = document.getElementById("resultOutput");

const errorContainer = document.getElementById("errorContainer");
const errorOutput = document.getElementById("errorOutput");

// Backend endpoint
const BACKEND_URL = "https://ironhalo-engine.onrender.com/config-strike";

submitBtn.addEventListener("click", async () => {
  // Hide previous UI
  resultContainer.classList.add("hidden");
  errorContainer.classList.add("hidden");

  // Canonical IronHalo sanitization
  const raw = configInput.value;
  const config = raw
    .replace(/\r\n/g, "\n")   // normalize CRLF → LF
    .replace(/\t/g, "  ")     // normalize tabs
    .replace(/\uFEFF/g, "")   // remove BOM
    .trim();                  // remove leading/trailing whitespace

  if (!config) {
    errorContainer.classList.remove("hidden");
    errorOutput.textContent = "Config cannot be empty.";
    return;
  }

  try {
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config })
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      errorContainer.classList.remove("hidden");
      errorOutput.textContent = data.error || `Backend error: ${response.status}`;
      return;
    }

    resultContainer.classList.remove("hidden");
    resultOutput.textContent = JSON.stringify(data, null, 2);

  } catch (err) {
    errorContainer.classList.remove("hidden");
    errorOutput.textContent = err.message || "Unknown error submitting config.";
  }
});
