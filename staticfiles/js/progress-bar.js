function updateProgressBar(currentIndex, total) {
  const bar = document.getElementById("progress-bar");
  if (!bar) return;

  const percentage = ((currentIndex / total) * 100).toFixed(2);
  bar.style.width = `${percentage}%`;

  // Animate the bar
  bar.classList.add("pulse");
  setTimeout(() => bar.classList.remove("pulse"), 300);
}

// Mini progress tracker (dots below the bar)
function updateMiniProgress(currentIndex, total) {
  const miniProgress = document.getElementById("mini-progress");
  if (!miniProgress) return;

  miniProgress.innerHTML = '';
  for (let i = 0; i < total; i++) {
    const dot = document.createElement("div");
    dot.classList.add("dot");
    if (i <= currentIndex) dot.classList.add("active");
    miniProgress.appendChild(dot);
  }
}

// Optional: Handle Enter key if needed
document.addEventListener("keydown", e => {
  if (e.key === "Enter") {
    // Optional: trigger the last clicked scale value or advance
    const lastClicked = document.querySelector(".scale-btn.last-clicked");
    if (lastClicked) lastClicked.click();
  }
});
