function showResults() {
  const container = document.querySelector(".question-container");

  // Calculate scores
  const anxiety = calculateAnxietyScore(answers);
  const depression = calculateDepressionScore(answers);
  const stress = calculateStressScore(answers);

  container.innerHTML = `
    <h3>Thanks for completing the test!</h3>
    <p>Here's how you scored:</p>
    <div class="results-summary">
      <div class="result-box"><strong>Anxiety:</strong> ${anxiety.score} (${anxiety.level})</div>
      <div class="result-box"><strong>Depression:</strong> ${depression.score} (${depression.level})</div>
      <div class="result-box"><strong>Stress:</strong> ${stress.score} (${stress.level})</div>
    </div>

    <div class="recommendations">
      <h4>Our Suggestions</h4>
      <ul>
        ${anxiety.score > 14 ? "<li>Consider guided breathing or journaling exercises.</li>" : ""}
        ${depression.score > 14 ? "<li>Try talking with peers or using a mood-tracking app.</li>" : ""}
        ${stress.score > 14 ? "<li>Short walks or breaks can ease tension.</li>" : ""}
        ${(anxiety.score > 14 || depression.score > 14 || stress.score > 14)
          ? "<li><strong>We recommend you speak with a guidance counselor.</strong></li>"
          : "<li>Keep up the great self-care work!</li>"}
      </ul>
    </div>

    <div class="schedule-btn-wrapper">
      <button id="schedule-btn"> Schedule a Counseling Session</button>
    </div>
    <div class="retry-wrapper">
      <button id="try-again-btn"> Try Again</button>
    </div>
  `;

  document.getElementById("schedule-btn").addEventListener("click", () => {
    window.location.href = "scheduler.html";
  });

  document.getElementById("try-again-btn").addEventListener("click", () => {
    const container = document.querySelector(".question-container");
    container.classList.remove("fade-in", "fade-out");
    void container.offsetWidth;
    container.classList.add("fade-out");

    setTimeout(() => {
      currentIndex = 0;
      answers.length = 0;
      renderQuizLayout();
      container.classList.remove("fade-out");
      void container.offsetWidth;
      container.classList.add("fade-in");
      loadQuestion();
    }, 500);
  });
}

function calculateAnxietyScore(answers) {
  const score = answers.slice(0, 7).reduce((a, b) => a + b, 0) * 2;
  return { score, level: getLevel(score) };
}

function calculateDepressionScore(answers) {
  const score = answers.slice(7, 14).reduce((a, b) => a + b, 0) * 2;
  return { score, level: getLevel(score) };
}

function calculateStressScore(answers) {
  const score = answers.slice(14, 21).reduce((a, b) => a + b, 0) * 2;
  return { score, level: getLevel(score) };
}

function getLevel(score) {
  if (score <= 9) return "Normal";
  if (score <= 13) return "Mild";
  if (score <= 20) return "Moderate";
  if (score <= 27) return "Severe";
  return "Extremely Severe";
}
