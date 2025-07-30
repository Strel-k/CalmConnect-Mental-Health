 const collegeData = {
      'all': {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Total Students',
          data: [450, 478, 520, 543, 567, 592],
          backgroundColor: 'rgba(46, 204, 113, 0.2)',
          borderColor: 'rgba(46, 204, 113, 1)',
          borderWidth: 2,
          fill: true
        }]
      },
      'engineering': {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Engineering Students',
          data: [120, 125, 135, 142, 148, 155],
          backgroundColor: 'rgba(52, 152, 219, 0.2)',
          borderColor: 'rgba(52, 152, 219, 1)',
          borderWidth: 2,
          fill: true
        }]
      },
      'medicine': {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Medicine Students',
          data: [85, 88, 92, 95, 98, 102],
          backgroundColor: 'rgba(231, 76, 60, 0.2)',
          borderColor: 'rgba(231, 76, 60, 1)',
          borderWidth: 2,
          fill: true
        }]
      }
    };

    // Initialize charts
    let collegeChart, combinedChart;

    function initializeCharts() {
      // College Chart
      const collegeCtx = document.getElementById('collegeChart').getContext('2d');
      collegeChart = new Chart(collegeCtx, {
        type: 'line',
        data: collegeData['all'],
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Student Enrollment Trends'
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });

      // Combined Chart
      const combinedCtx = document.getElementById('combinedCollegeChart').getContext('2d');
      combinedChart = new Chart(combinedCtx, {
        type: 'bar',
        data: {
          labels: ['Engineering', 'Medicine', 'Business', 'Arts & Sciences', 'Education', 'Law'],
          datasets: [{
            label: 'Average Wellness Score',
            data: [85, 92, 78, 88, 91, 83],
            backgroundColor: [
              'rgba(52, 152, 219, 0.8)',
              'rgba(231, 76, 60, 0.8)',
              'rgba(46, 204, 113, 0.8)',
              'rgba(155, 89, 182, 0.8)',
              'rgba(241, 196, 15, 0.8)',
              'rgba(230, 126, 34, 0.8)'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Average Wellness Scores by College'
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      });
    }

    // College selector change handler
    document.getElementById('collegeSelector').addEventListener('change', function() {
      const selectedCollege = this.value;
      if (collegeData[selectedCollege]) {
        collegeChart.data = collegeData[selectedCollege];
        collegeChart.update();
      }
    });

    // Export functions
    function exportChart(format) {
      const canvas = document.getElementById('collegeChart');
      if (format === 'png') {
        const link = document.createElement('a');
        link.download = 'college-chart.png';
        link.href = canvas.toDataURL();
        link.click();
      } else if (format === 'pdf') {
        alert('PDF export functionality would be implemented with additional libraries like jsPDF');
      }
    }

    function exportCombinedChart(format) {
      const canvas = document.getElementById('combinedCollegeChart');
      if (format === 'png') {
        const link = document.createElement('a');
        link.download = 'wellness-trends.png';
        link.href = canvas.toDataURL();
        link.click();
      } else if (format === 'pdf') {
        alert('PDF export functionality would be implemented with additional libraries like jsPDF');
      }
    }

    function exportToCSV() {
      const table = document.getElementById('dataTable');
      let csv = [];
      const rows = table.querySelectorAll('tr');
      
      for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
          row.push(cols[j].innerText);
        }
        csv.push(row.join(','));
      }
      
      const csvFile = new Blob([csv.join('\n')], { type: 'text/csv' });
      const downloadLink = document.createElement('a');
      downloadLink.download = 'wellness-data.csv';
      downloadLink.href = window.URL.createObjectURL(csvFile);
      downloadLink.click();
    }

    function exportToExcel() {
      alert('Excel export functionality would be implemented with libraries like SheetJS');
    }

    function printTable() {
      window.print();
    }

    // Initialize when page loads
    document.addEventListener('DOMContentLoaded', function() {
      initializeCharts();
    });