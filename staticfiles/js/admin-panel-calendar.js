document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("dashboard-calendar");

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    height: "auto",
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: ''
    },
    events: [
      {
        title: 'Student01 - Follow-up',
        start: '2025-06-04T10:00:00',
      },
      {
        title: 'Student02 - Evaluation',
        start: '2025-06-05T14:00:00',
      }
    ]
  });

  calendar.render();
});
