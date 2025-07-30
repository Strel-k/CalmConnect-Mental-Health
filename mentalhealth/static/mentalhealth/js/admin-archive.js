 const archiveButtons = document.querySelectorAll('.archive-btn');
    const archiveSections = document.querySelectorAll('.archive-section');

    archiveButtons.forEach(button => {
      button.addEventListener('click', () => {
        const targetType = button.getAttribute('data-type');
        
        // Update active button
        archiveButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Show corresponding section
        archiveSections.forEach(section => {
          section.classList.remove('active');
        });
        
        const targetSection = document.getElementById(targetType + 'Archive');
        if (targetSection) {
          targetSection.classList.add('active');
        }
      });
    });

    // Modal functionality
    function showArchiveModal(type, data) {
      const modal = document.getElementById('archive-modal');
      const modalTitle = document.getElementById('modal-title');
      const modalBody = document.getElementById('modal-body');
      
      let title = '';
      let content = '';
      
      switch(type) {
        case 'appointments':
          title = 'Appointment Details';
          content = `
            <p><strong>Student:</strong> ${data.student}</p>
            <p><strong>Date:</strong> ${data.date}</p>
            <p><strong>Time:</strong> ${data.time}</p>
            <p><strong>Counselor:</strong> ${data.counselor}</p>
            <p><strong>Reason:</strong> ${data.reason}</p>
          `;
          break;
        case 'dass21':
          title = 'DASS21 Results';
          content = `
            <p><strong>Student ID:</strong> ${data.studentId}</p>
            <p><strong>Assessment Date:</strong> ${data.date}</p>
            <p><strong>Depression Score:</strong> ${data.depression}</p>
            <p><strong>Anxiety Score:</strong> ${data.anxiety}</p>
            <p><strong>Stress Score:</strong> ${data.stress}</p>
            <p><strong>Risk Level:</strong> ${data.riskLevel}</p>
          `;
          break;
        case 'employees':
          title = 'Employee Record';
          content = `
            <p><strong>Name:</strong> ${data.name}</p>
            <p><strong>Employee ID:</strong> ${data.employeeId}</p>
            <p><strong>Position:</strong> ${data.position}</p>
            <p><strong>Department:</strong> ${data.department}</p>
            <p><strong>Employment Period:</strong> ${data.startDate} to ${data.endDate}</p>
          `;
          break;
      }
      
      modalTitle.textContent = title;
      modalBody.innerHTML = content;
      modal.style.display = 'block';
    }

    function closeArchiveModal() {
      document.getElementById('archive-modal').style.display = 'none';
    }

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
      const modal = document.getElementById('archive-modal');
      if (event.target === modal) {
        closeArchiveModal();
      }
    });

    // PDF Download functionality (placeholder)
    document.getElementById('downloadPdfBtn').addEventListener('click', () => {
      alert('PDF download functionality would be implemented here');
    });