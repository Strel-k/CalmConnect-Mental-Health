const collegePrograms = {
    CASS: [
      "Bachelor of Arts in Communication",
      "Bachelor of Arts in Political Science"
    ],
    CEN: [
      "Bachelor of Science in Civil Engineering",
      "Bachelor of Science in Computer Engineering"
    ],
    CBA: [
      "Bachelor of Science in Business Administration",
      "Bachelor of Science in Accountancy"
    ],
    COF: [
      "Bachelor of Science in Fisheries"
    ],
    CAG: [
      "Bachelor of Science in Agriculture",
      "Bachelor of Science in Agribusiness"
    ],
    CHSI: [
      "Bachelor of Science in Hospitality Management",
      "Bachelor of Science in Food Technology"
    ],
    CED: [
      "Bachelor of Secondary Education",
      "Bachelor of Elementary Education"
    ],
    COS: [
      "Bachelor of Science in Biology",
      "Bachelor of Science in Mathematics"
    ],
    CVSM: [
      "Doctor of Veterinary Medicine"
    ]
  };

  document.getElementById("college").addEventListener("change", function () {
    const college = this.value;
    const programSelect = document.getElementById("program");

    // Clear existing options
    programSelect.innerHTML = '<option value="">--Select Program--</option>';

    if (college && collegePrograms[college]) {
      collegePrograms[college].forEach(program => {
        const option = document.createElement("option");
        option.value = program;
        option.textContent = program;
        programSelect.appendChild(option);
      });
    }
  });