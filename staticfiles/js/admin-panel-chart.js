   const ctx = document.getElementById('overviewChart').getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Normal', 'Mild', 'Moderate', 'Severe', 'Extremely Severe'],
        datasets: [{
          data: [45, 23, 18, 10, 4],
          backgroundColor: [
            '#2ecc71',
            '#3498db',
            '#f1c40f',
            '#e67e22',
            '#e74c3c'
          ],
          borderWidth: 0,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true,
              font: {
                size: 12
              }
            }
          }
        }
      }
    });