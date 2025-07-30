  const archiveTypeSelector = document.getElementById("archiveType");

  archiveTypeSelector.addEventListener("change", function () {
    document.querySelectorAll(".archive-section").forEach(section => section.style.display = "none");

    const selected = this.value;
    document.getElementById(selected + "Archive").style.display = "block";
  });