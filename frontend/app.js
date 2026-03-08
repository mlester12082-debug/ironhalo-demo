const submitBtn = document.getElementById("submitBtn");
const configInput = document.getElementById("configInput");

const resultContainer = document.getElementById("resultContainer");
const resultOutput = document.getElementById("resultOutput");

const errorContainer = document.getElementById("errorContainer");
const errorOutput = document.getElementById("errorOutput");

// Your backend endpoint — update if needed
const BACKEND_URL = "https://ironhalo-engine.onrender.com/config-strike";

submitBtn.addEventListener("click", async () => {
  const configText = configInput.value.trim();

  resultContainer.classList.add("hidden");
  errorContainer.classList.add("hidden");

  if (!configText) {
    errorContainer.classList.remove("hidden");
    errorOutput.textContent = "Config cannot be empty.";
    return;
  }

  try {
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: configText })
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();

    resultContainer.classList.remove("hidden");
    resultOutput.textContent = JSON.stringify(data, null, 2);

  } catch (err) {
    errorContainer.classList.remove("hidden");
    errorOutput.textContent = err.message || "Unknown error submitting config.";
  }
});
