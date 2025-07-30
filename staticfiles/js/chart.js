document.addEventListener("DOMContentLoaded", function () {
  const chartData = [
    { college: "CASS", program: "Bachelor of Arts in Communication", anxiety: 19, depression: 20, stress: 20 },
    { college: "CASS", program: "Bachelor of Arts in Political Science", anxiety: 16, depression: 24, stress: 30 },
    { college: "CEN", program: "Bachelor of Science in Civil Engineering", anxiety: 29, depression: 10, stress: 11 },
    { college: "CEN", program: "Bachelor of Science in Computer Engineering", anxiety: 32, depression: 11, stress: 24 },
    { college: "CBA", program: "Bachelor of Science in Business Administration", anxiety: 21, depression: 18, stress: 28 },
    { college: "CBA", program: "Bachelor of Science in Accountancy", anxiety: 17, depression: 13, stress: 25 },
    { college: "COF", program: "Bachelor of Science in Fisheries", anxiety: 14, depression: 16, stress: 18 },
    { college: "CAG", program: "Bachelor of Science in Agribusiness", anxiety: 11, depression: 12, stress: 17 },
    { college: "CAG", program: "Bachelor of Science in Agriculture", anxiety: 18, depression: 19, stress: 20 },
    { college: "CHSI", program: "Bachelor of Science in Hospitality Management", anxiety: 10, depression: 15, stress: 22 },
    { college: "CHSI", program: "Bachelor of Science in Food Technology", anxiety: 13, depression: 16, stress: 21 },
    { college: "CED", program: "Bachelor of Secondary Education", anxiety: 25, depression: 22, stress: 27 },
    { college: "CED", program: "Bachelor of Elementary Education", anxiety: 20, depression: 21, stress: 23 },
    { college: "COS", program: "Bachelor of Science in Biology", anxiety: 26, depression: 28, stress: 31 },
    { college: "COS", program: "Bachelor of Science in Mathematics", anxiety: 15, depression: 14, stress: 19 },
    { college: "CVSM", program: "Doctor of Veterinary Medicine", anxiety: 30, depression: 27, stress: 32 }
  ];

  const ctx = document.getElementById("collegeChart").getContext("2d");
  let collegeChart = null;

  function renderCollegeChart(selectedCollege) {
    const filtered = chartData.filter(d => d.college === selectedCollege);

    const labels = filtered.map(d => d.program);
    const anxiety = filtered.map(d => d.anxiety);
    const depression = filtered.map(d => d.depression);
    const stress = filtered.map(d => d.stress);

    if (collegeChart) collegeChart.destroy();

    collegeChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Anxiety",
            data: anxiety,
            backgroundColor: "rgba(255, 99, 132, 0.6)"
          },
          {
            label: "Depression",
            data: depression,
            backgroundColor: "rgba(54, 162, 235, 0.6)"
          },
          {
            label: "Stress",
            data: stress,
            backgroundColor: "rgba(255, 206, 86, 0.6)"
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: 42
          }
        }
      }
    });
  }

  function renderCombinedChart() {
    const combined = {};

    chartData.forEach(d => {
      if (!combined[d.college]) {
        combined[d.college] = { anxiety: 0, depression: 0, stress: 0, count: 0 };
      }
      combined[d.college].anxiety += d.anxiety;
      combined[d.college].depression += d.depression;
      combined[d.college].stress += d.stress;
      combined[d.college].count += 1;
    });

    const labels = Object.keys(combined);
    const anxiety = labels.map(c => Math.round(combined[c].anxiety / combined[c].count));
    const depression = labels.map(c => Math.round(combined[c].depression / combined[c].count));
    const stress = labels.map(c => Math.round(combined[c].stress / combined[c].count));

    const ctxCombined = document.getElementById("combinedCollegeChart").getContext("2d");
    new Chart(ctxCombined, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Anxiety",
            data: anxiety,
            backgroundColor: "rgba(255, 99, 132, 0.6)"
          },
          {
            label: "Depression",
            data: depression,
            backgroundColor: "rgba(54, 162, 235, 0.6)"
          },
          {
            label: "Stress",
            data: stress,
            backgroundColor: "rgba(255, 206, 86, 0.6)"
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Average DASS21 Scores by College"
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: 40
          }
        }
      }
    });
  }

  // Event binding
  document.getElementById("collegeSelector").addEventListener("change", function () {
    const selectedCollege = this.value;
    if (selectedCollege) {
      renderCollegeChart(selectedCollege);
    }
  });

  // Render the combined overview initially
  renderCombinedChart();
});
