document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".archive-btn");
  const sections = {
    appointments: document.getElementById("appointmentsArchive"),
    dass21: document.getElementById("dass21Archive"),
    employees: document.getElementById("employeesArchive"),
  };

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      const type = button.getAttribute("data-type");

      // Hide all sections
      for (let key in sections) {
        if (sections[key]) {
          sections[key].style.display = "none";
        }
      }

      // Show the selected section
      if (sections[type]) {
        sections[type].style.display = "block";
      } else {
        console.warn(`No archive section found for type: ${type}`);
      }
    });
  });
});
