document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("admin-calendar");
  const modal = document.getElementById("appointmentModal");
  const form = document.getElementById("editAppointmentForm");

  const calendar = new FullCalendar.Calendar(calendarEl, {
  initialView: "dayGridMonth", // start in month view
  height: "auto",
  nowIndicator: true,
  selectable: true,
  editable: true,
  headerToolbar: {
    left: "prev,next today",
    center: "title",
    right: "" // remove view-switch buttons
  },
  events: [
    {
      id: "1",
      title: "Student01 Counseling",
      start: "2025-06-02T10:00:00",
      end: "2025-06-02T11:00:00",
      extendedProps: {
        studentId: "2023-00001",
        studentName: "Student01",
        college: "CASS",
        program: "Bachelor of Arts in Communication",
        counselor: "Ms. Rivera",
        reason: "Follow-up counseling"
      }
    },
    {
      id: "2",
      title: "Student02 Counseling",
      start: "2025-06-03T14:00:00",
      end: "2025-06-03T15:00:00",
      extendedProps: {
        studentId: "2023-00002",
        studentName: "Student02",
        college: "CEN",
        program: "BS Civil Engineering",
        counselor: "Mr. Santos",
        reason: "Initial consultation"
      }
    }
  ],
  eventClick: function (info) {
    showAppointmentModal(info.event);
  }
});

  calendar.render();
  window.calendar = calendar; 
function showAppointmentModal(event) {
  const modal = document.getElementById("appointmentModal");
  const form = document.getElementById("editAppointmentForm");

  if (!modal || !form) {
    console.error("Modal or form not found.");
    return;
  }

  // Fill in the form fields
  form.studentId.value = event.extendedProps?.studentId || "";
  form.studentName.value = event.extendedProps?.studentName || "";
  form.college.value = event.extendedProps?.college || "";
  form.program.value = event.extendedProps?.program || "";
  form.counselor.value = event.extendedProps?.counselor || "";
  form.reason.value = event.extendedProps?.reason || "";
  form.date.value = event.start.toISOString().split("T")[0];
  form.time.value = event.start.toTimeString().slice(0, 5);

  // Store reference to current event
  form.dataset.eventId = event.id;

  // Show the modal
  modal.style.display = "block";
}

  // Optional: close modal on outside click
  window.onclick = function (e) {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  };
});
function closeModal() {
  const modal = document.getElementById("appointmentModal");
  if (modal) modal.style.display = "none";
}

function archiveAppointment() {
  const modal = document.getElementById("appointmentModal");
  const form = document.getElementById("editAppointmentForm");
  const eventId = form.dataset.eventId;

  if (window.confirm("Are you sure you want to archive this appointment?")) {
    // Remove the event from the calendar
    const event = calendar.getEventById(eventId);
    if (event) event.remove();

    // Optionally log or send to archive database here

    // Hide modal
    closeModal();
  }
}

