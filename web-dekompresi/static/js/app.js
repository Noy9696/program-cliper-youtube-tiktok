// Global variables
let videoFile = null;
let videoFilePath = null;
let videoDuration = 0;
let backgroundAudioFile = null;
let backgroundAudioPath = null;
let soundEffects = [];
let currentJobId = null;

// Initialize
document.addEventListener("DOMContentLoaded", function () {
  initializeEventListeners();
  loadHistory();
});

function initializeEventListeners() {
  // Video upload
  const videoUploadZone = document.getElementById("videoUploadZone");
  const videoInput = document.getElementById("videoInput");

  videoUploadZone.addEventListener("click", () => videoInput.click());
  videoInput.addEventListener("change", handleVideoUpload);

  // Background audio
  const useBackgroundAudio = document.getElementById("useBackgroundAudio");
  useBackgroundAudio.addEventListener("change", toggleBackgroundAudio);

  const bgAudioUploadZone = document.getElementById("bgAudioUploadZone");
  const bgAudioInput = document.getElementById("bgAudioInput");

  bgAudioUploadZone.addEventListener("click", () => bgAudioInput.click());
  bgAudioInput.addEventListener("change", handleBackgroundAudioUpload);

  // Keep original audio checkbox
  const keepOriginalAudio = document.getElementById("keepOriginalAudio");
  keepOriginalAudio.addEventListener("change", toggleVolumeControls);

  // Volume sliders
  const originalVolume = document.getElementById("originalVolume");
  const backgroundVolume = document.getElementById("backgroundVolume");

  originalVolume.addEventListener("input", (e) => {
    document.getElementById("originalVolumeValue").textContent = e.target.value;
  });

  backgroundVolume.addEventListener("input", (e) => {
    document.getElementById("backgroundVolumeValue").textContent =
      e.target.value;
  });

  // Sound effects
  const addSoundEffect = document.getElementById("addSoundEffect");
  addSoundEffect.addEventListener("click", openSoundEffectModal);

  // Modal
  const modalCloses = document.querySelectorAll(".modal-close");
  modalCloses.forEach((close) => {
    close.addEventListener("click", closeSoundEffectModal);
  });

  // Sound effect modal
  const sfxUploadZone = document.getElementById("sfxUploadZone");
  const sfxInput = document.getElementById("sfxInput");

  sfxUploadZone.addEventListener("click", () => sfxInput.click());
  sfxInput.addEventListener("change", handleSfxUpload);

  const sfxVolume = document.getElementById("sfxVolume");
  sfxVolume.addEventListener("input", (e) => {
    document.getElementById("sfxVolumeValue").textContent = e.target.value;
  });

  const sfxUseFade = document.getElementById("sfxUseFade");
  sfxUseFade.addEventListener("change", (e) => {
    document.getElementById("sfxFadeConfig").style.display = e.target.checked
      ? "block"
      : "none";
  });

  const addSfxBtn = document.getElementById("addSfxBtn");
  addSfxBtn.addEventListener("click", addSoundEffectToList);

  // Process button
  const processBtn = document.getElementById("processBtn");
  processBtn.addEventListener("click", startProcessing);

  // Result buttons
  const downloadBtn = document.getElementById("downloadBtn");
  const processAnotherBtn = document.getElementById("processAnotherBtn");

  downloadBtn.addEventListener("click", downloadResult);
  processAnotherBtn.addEventListener("click", resetForm);
}

async function handleVideoUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  videoFile = file;

  const formData = new FormData();
  formData.append("video", file);

  try {
    const response = await fetch("/upload_video", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.success) {
      videoFilePath = data.filepath;
      videoDuration = data.info.duration;

      // Update video info
      document.getElementById("videoResolution").textContent =
        `${data.info.width} × ${data.info.height}`;
      document.getElementById("videoDuration").textContent =
        `${data.info.duration.toFixed(2)}s`;
      document.getElementById("videoFPS").textContent = data.info.fps;
      document.getElementById("videoSize").textContent =
        `${data.info.size_mb} MB`;
      document.getElementById("videoAudio").textContent = data.info.has_audio
        ? "✓ Yes"
        : "✗ No";

      document.getElementById("videoInfo").style.display = "block";

      // Update preview
      const videoPreview = document.getElementById("videoPreview");
      videoPreview.src = data.url;
      videoPreview.style.display = "block";
      document.getElementById("videoPreviewPlaceholder").style.display = "none";

      // Enable process button
      document.getElementById("processBtn").disabled = false;

      showNotification("✅ Video uploaded successfully!", "success");
    } else {
      showNotification("❌ Upload failed: " + data.error, "error");
    }
  } catch (error) {
    showNotification("❌ Upload error: " + error.message, "error");
  }
}

function toggleBackgroundAudio() {
  const useBackground = document.getElementById("useBackgroundAudio").checked;
  document.getElementById("backgroundAudioConfig").style.display = useBackground
    ? "block"
    : "none";
}

async function handleBackgroundAudioUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  backgroundAudioFile = file;

  const formData = new FormData();
  formData.append("audio", file);

  try {
    const response = await fetch("/upload_audio", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.success) {
      backgroundAudioPath = data.filepath;

      document.getElementById("bgAudioName").textContent = file.name;
      document.getElementById("bgAudioInfo").style.display = "block";

      showNotification("✅ Background audio uploaded!", "success");
    } else {
      showNotification("❌ Upload failed: " + data.error, "error");
    }
  } catch (error) {
    showNotification("❌ Upload error: " + error.message, "error");
  }
}

function toggleVolumeControls() {
  const keepOriginal = document.getElementById("keepOriginalAudio").checked;
  document.getElementById("volumeControls").style.display = keepOriginal
    ? "block"
    : "none";
}

function openSoundEffectModal() {
  document.getElementById("soundEffectModal").style.display = "flex";
}

function closeSoundEffectModal() {
  document.getElementById("soundEffectModal").style.display = "none";
  resetSfxForm();
}

function resetSfxForm() {
  document.getElementById("sfxInput").value = "";
  document.getElementById("sfxInfo").style.display = "none";
  document.getElementById("sfxTimestamp").value = "";
  document.getElementById("sfxDuration").value = "";
  document.getElementById("sfxVolume").value = 100;
  document.getElementById("sfxVolumeValue").textContent = 100;
  document.getElementById("sfxUseFade").checked = false;
  document.getElementById("sfxFadeConfig").style.display = "none";
}

let currentSfxFile = null;
let currentSfxPath = null;

async function handleSfxUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  currentSfxFile = file;

  const formData = new FormData();
  formData.append("audio", file);

  try {
    const response = await fetch("/upload_audio", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.success) {
      currentSfxPath = data.filepath;

      document.getElementById("sfxName").textContent = file.name;
      document.getElementById("sfxInfo").style.display = "block";
    } else {
      showNotification("❌ Upload failed: " + data.error, "error");
    }
  } catch (error) {
    showNotification("❌ Upload error: " + error.message, "error");
  }
}

function addSoundEffectToList() {
  if (!currentSfxPath) {
    showNotification("❌ Please upload a sound file first!", "error");
    return;
  }

  const timestamp = parseFloat(document.getElementById("sfxTimestamp").value);
  if (isNaN(timestamp) || timestamp < 0 || timestamp >= videoDuration) {
    showNotification(
      `❌ Timestamp must be between 0 and ${videoDuration.toFixed(2)}`,
      "error",
    );
    return;
  }

  const duration = document.getElementById("sfxDuration").value;
  const volume = parseInt(document.getElementById("sfxVolume").value);
  const useFade = document.getElementById("sfxUseFade").checked;
  const fadeDuration = useFade
    ? parseFloat(document.getElementById("sfxFadeDuration").value)
    : 0;

  const sfx = {
    path: currentSfxPath,
    name: currentSfxFile.name,
    timestamp: timestamp,
    duration: duration ? parseFloat(duration) : null,
    volume: volume,
    fade_duration: fadeDuration,
  };

  soundEffects.push(sfx);
  renderSoundEffects();
  closeSoundEffectModal();
  showNotification("✅ Sound effect added!", "success");
}

function renderSoundEffects() {
  const list = document.getElementById("soundEffectsList");

  if (soundEffects.length === 0) {
    list.innerHTML = "";
    return;
  }

  list.innerHTML = soundEffects
    .map(
      (sfx, index) => `
        <div class="sound-effect-item">
            <div class="sound-effect-info">
                <h4>🎵 ${sfx.name}</h4>
                <p>⏱️ At ${sfx.timestamp}s · 🔊 ${sfx.volume}% · 
                   ${sfx.duration ? `⏱️ ${sfx.duration}s` : "Full duration"}
                   ${sfx.fade_duration > 0 ? ` · 🎚️ Fade ${sfx.fade_duration}s` : ""}</p>
            </div>
            <button class="sound-effect-remove" onclick="removeSoundEffect(${index})">
                🗑️ Remove
            </button>
        </div>
    `,
    )
    .join("");
}

function removeSoundEffect(index) {
  soundEffects.splice(index, 1);
  renderSoundEffects();
  showNotification("✅ Sound effect removed", "success");
}

async function startProcessing() {
  if (!videoFilePath) {
    showNotification("❌ Please upload a video first!", "error");
    return;
  }

  // Get selected preset
  const preset = document.querySelector('input[name="preset"]:checked').value;

  // Build config
  const config = {
    input_file: videoFilePath,
    preset: preset,
    use_background_audio: document.getElementById("useBackgroundAudio").checked,
    keep_original_audio: document.getElementById("keepOriginalAudio").checked,
    original_volume: parseInt(document.getElementById("originalVolume").value),
    background_volume: parseInt(
      document.getElementById("backgroundVolume").value,
    ),
    sound_effects: soundEffects,
  };

  if (config.use_background_audio && backgroundAudioPath) {
    config.background_audio_file = backgroundAudioPath;
  }

  try {
    const response = await fetch("/process", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });

    const data = await response.json();

    if (data.success) {
      currentJobId = data.job_id;

      // Show processing card
      document.getElementById("processingCard").style.display = "block";
      document.getElementById("resultCard").style.display = "none";
      document.getElementById("processBtn").disabled = true;

      // Start polling status
      pollStatus();

      showNotification("✅ Processing started!", "success");
    } else {
      showNotification("❌ Failed to start processing", "error");
    }
  } catch (error) {
    showNotification("❌ Error: " + error.message, "error");
  }
}

async function pollStatus() {
  if (!currentJobId) return;

  try {
    const response = await fetch(`/status/${currentJobId}`);
    const data = await response.json();

    // Update progress
    document.getElementById("progressFill").style.width = data.progress + "%";
    document.getElementById("progressPercent").textContent = data.progress;
    document.getElementById("progressMessage").textContent = data.message;

    if (data.status === "completed") {
      // Show result
      document.getElementById("processingCard").style.display = "none";
      document.getElementById("resultCard").style.display = "block";

      // Update result info
      document.getElementById("outputSize").textContent =
        data.output_size_mb + " MB";
      document.getElementById("compressionRatio").textContent =
        data.compression_ratio >= 0
          ? `${data.compression_ratio}% reduced`
          : `${Math.abs(data.compression_ratio)}% increased`;
      document.getElementById("processingTime").textContent =
        data.processing_time + "s";

      // Update preview
      const resultPreview = document.getElementById("resultPreview");
      resultPreview.src = data.output_url;

      // Set download URL
      document.getElementById("downloadBtn").dataset.filename =
        data.output_file;

      // Reload history
      loadHistory();

      showNotification("✅ Processing complete!", "success");
    } else if (data.status === "error") {
      document.getElementById("processingCard").style.display = "none";
      showNotification("❌ Processing failed: " + data.message, "error");
      document.getElementById("processBtn").disabled = false;
    } else {
      // Continue polling
      setTimeout(pollStatus, 1000);
    }
  } catch (error) {
    console.error("Status poll error:", error);
    setTimeout(pollStatus, 2000);
  }
}

function downloadResult() {
  const filename = document.getElementById("downloadBtn").dataset.filename;
  if (filename) {
    window.location.href = `/download/${filename}`;
  }
}

function resetForm() {
  location.reload();
}

async function loadHistory() {
  try {
    const response = await fetch("/history");
    const data = await response.json();

    const historyList = document.getElementById("historyList");

    if (data.files.length === 0) {
      historyList.innerHTML = '<p class="text-muted">No history yet</p>';
      return;
    }

    historyList.innerHTML = data.files
      .map(
        (file) => `
            <div class="history-item">
                <div class="history-info">
                    <h4>📹 ${file.filename}</h4>
                    <p>📦 ${file.size_mb} MB · 🕒 ${file.created}</p>
                </div>
                <div class="history-actions">
                    <button onclick="previewHistory('${file.url}')">👁️ Preview</button>
                    <button onclick="downloadHistory('${file.filename}')">📥 Download</button>
                </div>
            </div>
        `,
      )
      .join("");
  } catch (error) {
    console.error("Failed to load history:", error);
  }
}

function previewHistory(url) {
  const resultPreview = document.getElementById("resultPreview");
  resultPreview.src = url;
  resultPreview.scrollIntoView({ behavior: "smooth" });
}

function downloadHistory(filename) {
  window.location.href = `/download/${filename}`;
}

function showNotification(message, type = "info") {
  // Simple notification (you can use a library like toastr for better UX)
  alert(message);
}
