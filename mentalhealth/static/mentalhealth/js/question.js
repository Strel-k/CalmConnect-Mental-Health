function renderQuizLayout() {
  const container = document.querySelector(".question-container");
  container.classList.remove("fade-out");
  container.classList.add("fade-in");

  container.innerHTML = `
    <div class="encouragement-msg" style="display: none;"></div>
    <h3 id="question-text">Loading question...</h3>
    <div class="scale-options">
      <button class="scale-btn" data-value="0">😐 0</button>
      <button class="scale-btn" data-value="1">🙂 1</button>
      <button class="scale-btn" data-value="2">😕 2</button>
      <button class="scale-btn" data-value="3">😟 3</button>
    </div>
    <div class="progress-container">
      <div class="progress-bar" id="progress-bar"></div>
    </div>
    <div class="question-progress">
      <p id="progress">1 / 21</p>
    </div>
  `;

  document.querySelectorAll(".scale-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const value = parseInt(btn.getAttribute("data-value"));
      answers.push(value);
      currentIndex++;
      loadQuestion();
    });
  });
}

const encouragements = [
  "You're doing great! 💪",
  "Take your time — this is all about you. 🌱",
  "Almost there! Keep going! 🚶",
  "Thank you for taking this step. 💚",
  "You're not alone in this journey. 🌈"
];

let currentIndex = 0;
const answers = [];
const questions = [
  {
    text: "I found it hard to wind down.",
    next: [1, 2, 3, 4] // branching example
  },
  {
    text: "I tended to over-react to situations.",
    next: [5, 5, 5, 5]
  },
  {
    text: "I felt that I was using a lot of nervous energy.",
    next: [5, 5, 5, 5]
  },
  {
    text: "I found myself getting agitated.",
    next: [5, 5, 5, 5]
  },
  {
    text: "I found it difficult to relax.",
    next: [5, 5, 5, 5]
  },
  { text: "I felt down-hearted and blue.", next: [] },
  { text: "I had trouble relaxing.", next: [] },
  { text: "I felt I had nothing to look forward to.", next: [] },
  { text: "I experienced trembling (e.g. in the hands).", next: [] },
  { text: "I was unable to become enthusiastic about anything.", next: [] },
  { text: "I felt I wasn't worth much as a person.", next: [] },
  { text: "I felt that life was meaningless.", next: [] },
  { text: "I felt I was close to panic.", next: [] }
];

function renderQuizLayout() {
  const container = document.querySelector(".question-container");
  container.classList.remove("fade-out");
  container.classList.add("fade-in");
  container.innerHTML = `
    <div class="encouragement-msg" style="display: none;"></div>
    <h3 id="question-text">Loading question...</h3>
    <div class="scale-options">
      <button class="scale-btn" data-value="0">😐 0</button>
      <button class="scale-btn" data-value="1">🙂 1</button>
      <button class="scale-btn" data-value="2">😕 2</button>
      <button class="scale-btn" data-value="3">😟 3</button>
    </div>
    <div class="progress-container">
      <div class="progress-bar" id="progress-bar"></div>
    </div>
    <div class="question-progress">
      <p id="progress">1 / ${questions.length}</p>
    </div>
  `;

  document.querySelectorAll(".scale-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const value = parseInt(btn.getAttribute("data-value"));
      answers.push(value);
      const encouragement = encouragements[Math.floor(Math.random() * encouragements.length)];
      const encouragementBox = document.querySelector(".encouragement-msg");
      encouragementBox.textContent = encouragement;
      encouragementBox.style.display = "block";

      const nextIndex = questions[currentIndex].next?.[value] ?? currentIndex + 1;
      currentIndex = nextIndex;
      setTimeout(() => {
        loadQuestion();
      }, 700);
    });
  });
}

function loadQuestion() {
  if (currentIndex >= questions.length) {
    showResults();
    return;
  }

  document.getElementById("question-text").textContent = questions[currentIndex].text;
  document.getElementById("progress").textContent = `${currentIndex + 1} / ${questions.length}`;
  updateProgressBar(currentIndex, questions.length);
}

renderQuizLayout();
loadQuestion();
