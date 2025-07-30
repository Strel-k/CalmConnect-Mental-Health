document.addEventListener("DOMContentLoaded", function () {
  const today = new Date();
  const addDays = (days) => {
    const date = new Date(today);
    date.setDate(date.getDate() + days);
    return date.toISOString().split("T")[0];
  };

  // Counselor schedule data
 const counselorSchedules = {
  counselor1: [
    "June 5, 10:00 AM - 11:00 AM",
    "June 6, 2:00 PM - 3:00 PM"
  ],
  counselor2: [
    "June 7, 9:00 AM - 10:30 AM",
    "June 8, 1:00 PM - 2:30 PM"
  ],
  counselor3: [
    "June 7, 9:00 AM - 10:30 AM",
    "June 8, 1:00 PM - 2:30 PM"
  ]
};

const slotList = document.querySelector(".slot-list");

document.querySelectorAll(".counselor-card").forEach(card => {
  card.addEventListener("click", () => {
    const selected = card.dataset.counselor;
    document.querySelectorAll(".counselor-card").forEach(c => c.classList.remove("active"));
    card.classList.add("active");

    // Clear and populate new slots
    slotList.innerHTML = "";
    counselorSchedules[selected].forEach(slot => {
      const li = document.createElement("li");
      li.textContent = slot;
      li.classList.add("slot-item");
      li.addEventListener("click", () => {
        document.getElementById("slot-display").value = slot;
        document.getElementById("booking-modal").style.display = "block";
      });
      slotList.appendChild(li);
    });
  });
});

  const timeSlotsContainer = document.getElementById("time-slots");
  const modal = document.getElementById("appointmentModal");
  const confirmModal = document.getElementById("confirmationModal");
  const form = document.getElementById("appointmentForm");
  let selectedSession = null;

  // Display available time slots for a counselor
  function showSlots(counselorId) {
    const schedule = counselorSchedules[counselorId];
    timeSlotsContainer.innerHTML = "";

    schedule.forEach((slot, index) => {
      const card = document.createElement("div");
      card.className = "slot-card";
      card.innerHTML = `
        <h4>${slot.date}</h4>
        <p>${slot.time}</p>
        <button class="book-btn" data-counselor="${counselorId}" data-date="${slot.date}" data-time="${slot.time}">
          Book Session
        </button>
      `;
      timeSlotsContainer.appendChild(card);
    });

    // Re-attach click handlers to new buttons
    document.querySelectorAll(".book-btn").forEach(button => {
      button.addEventListener("click", () => {
        selectedSession = {
          counselor: button.dataset.counselor,
          date: button.dataset.date,
          time: button.dataset.time
        };
        modal.style.display = "block";
      });
    });
  }

  // Counselor selection card
  document.querySelectorAll(".counselor-card").forEach(card => {
    card.addEventListener("click", () => {
      document.querySelectorAll(".counselor-card").forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      const selected = card.dataset.counselor;
      showSlots(selected);
    });
  });

  // Trigger default counselor on load
  document.querySelector(".counselor-card[data-counselor='counselor1']").click();

  // Handle form submission
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    modal.style.display = "none";
    document.getElementById("confirmationModal").style.display = "block";

    // Optionally you can show details inside the confirmation modal dynamically
    const summary = document.getElementById("appointment-summary");
    if (summary && selectedSession) {
      summary.innerHTML = `
        <p><strong>Date:</strong> ${selectedSession.date}</p>
        <p><strong>Time:</strong> ${selectedSession.time}</p>
        <p><strong>Counselor:</strong> ${selectedSession.counselor === 'counselor1' ? 'Ms. Rivera' : 'Mr. Santos'}</p>
      `;
    }

    form.reset();
  });
});
document.getElementById("close-modal").addEventListener("click", () => {
  document.getElementById("booking-modal").style.display = "none";
});
// Modal close function for confirmation
function closeConfirmationModal() {
  document.getElementById("confirmationModal").style.display = "none";
}
