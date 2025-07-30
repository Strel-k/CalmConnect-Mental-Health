const form = document.getElementById("booking-form");

form.addEventListener("submit", function (e) {
  e.preventDefault();

  // Hide modal
  document.getElementById("booking-modal").style.display = "none";

  // Show confirmation
  document.getElementById("confirmationModal").style.display = "block";

  form.reset();
});
