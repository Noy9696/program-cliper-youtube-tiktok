let sceneCount = 0;
let sourceVideo = null;
let processingInterval = null;

// Initialize
document.addEventListener("DOMContentLoaded", function () {
  sourceVideo = document.getElementById("sourceVideo");

  // Update current time display
  sourceVideo.addEventListener("timeupdate", function () {
    document.getElementById("currentTime").textContent = formatTime(
      sourceVideo.currentTime,
    );
  });

  // Update total duration
  sourceVideo.addEventListener("loadedmetadata", function () {
    document.getElementById("totalDuration").textContent = formatTime(
      sourceVideo.duration,
    );
  });

  // Load video info
  loadVideoInfo();

  // Add initial scene row
  addSceneRow();
});

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);

  if (h > 0) {
    return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function loadVideoInfo() {
  fetch("/api/video-info")
    .then((response) => response.json())
    .then((data) => {
      console.log("Video info:", data);
    })
    .catch((error) => {
      console.error("Error loading video info:", error);
    });
}

function useCurrentTime() {
  const currentTime = formatTime(sourceVideo.currentTime);

  // Cari row terakhir yang kosong atau buat baru
  const rows = document.querySelectorAll("#sceneTableBody tr");
  let targetRow = null;

  for (let row of rows) {
    const input = row.querySelector('input[name="start_time"]');
    if (!input.value) {
      targetRow = row;
      break;
    }
  }

  if (!targetRow && rows.length > 0) {
    targetRow = rows[rows.length - 1];
  }

  if (targetRow) {
    targetRow.querySelector('input[name="start_time"]').value = currentTime;
    targetRow.querySelector('input[name="start_time"]').focus();
  }
}

function addSceneRow() {
  sceneCount++;
  const tbody = document.getElementById("sceneTableBody");

  const row = document.createElement("tr");
  row.innerHTML = `
        <td>${sceneCount}</td>
        <td><input type="text" name="start_time" placeholder="MM:SS atau HH:MM:SS" required></td>
        <td><input type="number" name="duration" placeholder="detik" min="1" required></td>
        <td>
            <select name="gamer_position">
                <option value="atas">Atas</option>
                <option value="bawah">Bawah</option>
            </select>
        </td>
        <td>
            <select name="blink_enabled" onchange="toggleBlinkInputs(this)">
                <option value="false">Tidak</option>
                <option value="true">Ya</option>
            </select>
        </td>
        <td><input type="number" name="blink_start" placeholder="detik" min="0" disabled></td>
        <td><input type="number" name="blink_end" placeholder="detik" min="0" disabled></td>
        <td><button class="btn-delete" onclick="deleteRow(this)">🗑️</button></td>
    `;

  tbody.appendChild(row);
}

function deleteRow(btn) {
  const row = btn.closest("tr");
  row.remove();

  // Renumber rows
  const rows = document.querySelectorAll("#sceneTableBody tr");
  rows.forEach((row, index) => {
    row.querySelector("td:first-child").textContent = index + 1;
  });

  sceneCount = rows.length;
}

function toggleBlinkInputs(select) {
  const row = select.closest("tr");
  const blinkStart = row.querySelector('input[name="blink_start"]');
  const blinkEnd = row.querySelector('input[name="blink_end"]');

  if (select.value === "true") {
    blinkStart.disabled = false;
    blinkEnd.disabled = false;
  } else {
    blinkStart.disabled = true;
    blinkEnd.disabled = true;
    blinkStart.value = "";
    blinkEnd.value = "";
  }
}

function getSceneData() {
  const rows = document.querySelectorAll("#sceneTableBody tr");
  const scenes = [];

  rows.forEach((row) => {
    const startTime = row.querySelector('input[name="start_time"]').value;
    const duration = row.querySelector('input[name="duration"]').value;
    const gamerPosition = row.querySelector(
      'select[name="gamer_position"]',
    ).value;
    const blinkEnabled =
      row.querySelector('select[name="blink_enabled"]').value === "true";
    const blinkStart = row.querySelector('input[name="blink_start"]').value;
    const blinkEnd = row.querySelector('input[name="blink_end"]').value;

    if (startTime && duration) {
      scenes.push({
        start_time: startTime,
        duration: parseInt(duration),
        gamer_position: gamerPosition,
        blink_enabled: blinkEnabled,
        blink_start: blinkEnabled ? parseInt(blinkStart) : 0,
        blink_end: blinkEnabled ? parseInt(blinkEnd) : 0,
      });
    }
  });

  return scenes;
}

function startProcessing() {
  const scenes = getSceneData();

  if (scenes.length === 0) {
    alert("❌ Tambahkan minimal 1 scene!");
    return;
  }

  // Validate scenes
  for (let i = 0; i < scenes.length; i++) {
    if (scenes[i].blink_enabled) {
      if (scenes[i].blink_start >= scenes[i].blink_end) {
        alert(
          `❌ Scene ${i + 1}: Blink start harus lebih kecil dari blink end!`,
        );
        return;
      }
      if (scenes[i].blink_end > scenes[i].duration) {
        alert(`❌ Scene ${i + 1}: Blink end tidak boleh lebih dari duration!`);
        return;
      }
    }
  }

  const transitionType = document.getElementById("transitionType").value;
  const mergeMethod = document.getElementById("mergeMethod").value;

  // Show progress section
  document.getElementById("progressSection").style.display = "block";
  document.getElementById("resultsSection").style.display = "none";

  // Disable generate button
  const btn = document.querySelector(".btn-generate");
  btn.disabled = true;
  btn.textContent = "⏳ Processing...";

  // Prepare scene progress list
  const progressList = document.getElementById("sceneProgressList");
  progressList.innerHTML = "";

  scenes.forEach((scene, index) => {
    const item = document.createElement("div");
    item.className = "scene-progress-item";
    item.id = `scene-progress-${index + 1}`;
    item.innerHTML = `
            <strong>Scene ${index + 1}</strong>: ${scene.start_time} → ${scene.duration}s
            <span class="status">⏳ Waiting...</span>
        `;
    progressList.appendChild(item);
  });

  // Start processing
  fetch("/api/process", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      scenes: scenes,
      transition_type: transitionType,
      merge_method: mergeMethod,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "started") {
        // Start polling status
        pollProcessingStatus();
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("❌ Error starting process: " + error);
      btn.disabled = false;
      btn.textContent = "🚀 Generate Video";
    });
}

function pollProcessingStatus() {
  processingInterval = setInterval(() => {
    fetch("/api/status")
      .then((response) => response.json())
      .then((status) => {
        updateProgressUI(status);

        if (status.status === "completed" || status.status === "error") {
          clearInterval(processingInterval);

          const btn = document.querySelector(".btn-generate");
          btn.disabled = false;
          btn.textContent = "🚀 Generate Video";

          if (status.status === "completed") {
            showResults(status);
          } else {
            alert("❌ Processing error: " + status.message);
          }
        }
      })
      .catch((error) => {
        console.error("Error polling status:", error);
      });
  }, 1000); // Poll every second
}

function showPage(page) {
  document.getElementById("page-editor").style.display =
    page === "editor" ? "block" : "none";
  document.getElementById("page-youtube").style.display =
    page === "youtube" ? "block" : "none";

  document
    .querySelectorAll(".nav-btn")
    .forEach((b) => b.classList.remove("active"));
  event.target.classList.add("active");
}

async function startYoutubeDownload() {
  const url = document.getElementById("ytUrl").value;
  if (!url) return alert("Masukkan link YouTube");

  await fetch("/api/youtube/download", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  document.getElementById("ytProgressText").innerText = "Starting...";

  const timer = setInterval(async () => {
    const res = await fetch("/api/youtube/progress");
    const p = await res.json();

    let percent = 0;
    if (p.percent) {
      percent = parseFloat(p.percent.replace("%", "")) || 0;
    }
    percent = Math.min(Math.max(percent, 0), 100);
    document.getElementById("ytProgressFill").style.width = percent + "%";

    document.getElementById("ytProgressText").innerText =
      `⬇ ${p.percent} | ⚡ ${p.speed} | ⏳ ${p.eta}`;

    if (p.status === "done") {
      clearInterval(timer);

      const video = document.getElementById("sourceVideo");

      video.pause();
      video.removeAttribute("src");

      setTimeout(() => {
        video.src = "/source-video?t=" + Date.now();
        video.style.display = "block";
        video.load();
      }, 500);

      video.onloadedmetadata = () => {
        console.log("Video ready:", video.duration);
      };

      alert("Download selesai! Video siap dipreview & diproses.");
    }
  }, 1000);
}

function updateProgressUI(status) {
  // Update progress bar
  const progressFill = document.getElementById("progressFill");
  progressFill.style.width = status.progress + "%";
  progressFill.textContent = status.progress + "%";

  // Update message
  document.getElementById("progressMessage").textContent = status.message;
  document.getElementById("progressScene").textContent =
    `Scene: ${status.current_scene}/${status.total_scenes}`;

  // Update scene progress items
  if (status.current_scene > 0) {
    for (let i = 1; i <= status.current_scene; i++) {
      const item = document.getElementById(`scene-progress-${i}`);
      if (item) {
        if (i < status.current_scene) {
          item.classList.remove("processing");
          item.classList.add("completed");
          item.querySelector(".status").textContent = "✅ Completed";
        } else if (i === status.current_scene) {
          item.classList.add("processing");
          item.querySelector(".status").textContent = "⏳ Processing...";
        }
      }
    }
  }
}

function showResults(status) {
  const resultsSection = document.getElementById("resultsSection");
  resultsSection.style.display = "block";

  // Show final video
  const finalVideoResult = document.getElementById("finalVideoResult");
  if (status.final_output) {
    finalVideoResult.innerHTML = `
            <div class="video-card">
                <h4>🎞️ ${status.final_output.filename}</h4>
                <video controls>
                    <source src="/video/${status.final_output.filename}" type="video/mp4">
                </video>
                <div class="info">
                    Size: ${(status.final_output.size / 1024 / 1024).toFixed(2)} MB
                </div>
                <a href="/api/download/${status.final_output.filename}" class="btn-download">
                    ⬇️ Download
                </a>
            </div>
        `;
  }

  // Show scene videos
  const sceneResults = document.getElementById("sceneResults");
  sceneResults.innerHTML = "";

  status.scene_files.forEach((file) => {
    const card = document.createElement("div");
    card.className = "video-card";
    card.innerHTML = `
            <h4>Scene ${file.number}</h4>
            <video controls>
                <source src="/video/${file.filename}" type="video/mp4">
            </video>
            <div class="info">
                Size: ${(file.size / 1024 / 1024).toFixed(2)} MB
            </div>
            <a href="/api/download/${file.filename}" class="btn-download">
                ⬇️ Download
            </a>
        `;
    sceneResults.appendChild(card);
  });

  // Scroll to results
  resultsSection.scrollIntoView({ behavior: "smooth" });
}

function loadVideoLibrary() {
  fetch("/api/videos")
    .then((res) => res.json())
    .then((videos) => {
      const list = document.getElementById("videoList");
      list.innerHTML = "";

      videos.forEach((v) => {
        const card = document.createElement("div");
        card.className = "video-card";
        card.innerHTML = `
          <video src="/video/${v.filename}" muted></video>
          <p>${v.filename}</p>
          <button onclick="useAsSource('${v.filename}')">
            🎯 Gunakan
          </button>
        `;
        list.appendChild(card);
      });
    });
}

function useAsSource(filename) {
  fetch("/api/set-source", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename }),
  }).then(() => {
    const video = document.getElementById("sourceVideo");
    video.src = "/source-video?t=" + Date.now();
    video.load();
  });
}
