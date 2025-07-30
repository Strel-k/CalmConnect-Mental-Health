// Fixed Archive Simulation JavaScript
class ArchiveManager {
  constructor() {
    this.activeRecords = {
      appointments: [
        {
          id: 'apt-001',
          student: 'Sarah Johnson',
          studentId: 'STU-2021-0145',
          college: 'College of Liberal Arts',
          program: 'Psychology (BS)',
          date: '2025-06-05',
          time: '2:00 PM',
          counselor: 'Dr. Maria Santos',
          reason: 'Anxiety management and coping strategies for exam periods',
          status: 'active'
        },
        {
          id: 'apt-002',
          student: 'Mike Chen',
          studentId: 'STU-2022-0298',
          college: 'College of Engineering',
          program: 'Computer Science (BS)',
          date: '2025-06-06',
          time: '10:30 AM',
          counselor: 'Prof. John Martinez',
          reason: 'Academic pressure and time management issues',
          status: 'active'
        },
        {
          id: 'apt-003',
          student: 'Emma Wilson',
          studentId: 'STU-2020-0087',
          college: 'College of Arts and Sciences',
          program: 'English Literature (BA)',
          date: '2025-06-07',
          time: '9:00 AM',
          counselor: 'Dr. Patricia Lee',
          reason: 'Depression counseling and mental health support',
          status: 'active'
        },
        {
          id: 'apt-004',
          student: 'James Rodriguez',
          studentId: 'STU-2023-0156',
          college: 'College of Business',
          program: 'Business Administration (BS)',
          date: '2025-06-08',
          time: '3:30 PM',
          counselor: 'Dr. Lisa Wong',
          reason: 'Career guidance and academic planning',
          status: 'active'
        },
        {
          id: 'apt-005',
          student: 'Anna Kim',
          studentId: 'STU-2022-0089',
          college: 'College of Health Sciences',
          program: 'Nursing (BSN)',
          date: '2025-06-10',
          time: '11:00 AM',
          counselor: 'Prof. Robert Davis',
          reason: 'Stress management and work-life balance',
          status: 'active'
        }
      ],
      dass21: [
        {
          id: 'dass-001',
          studentId: '2023-00004',
          dateCompleted: '2025-06-03',
          depression: 6,
          anxiety: 8,
          stress: 7,
          riskLevel: 'Mild',
          status: 'active'
        },
        {
          id: 'dass-002',
          studentId: '2023-00005',
          dateCompleted: '2025-06-02',
          depression: 12,
          anxiety: 14,
          stress: 13,
          riskLevel: 'Moderate',
          status: 'active'
        }
      ],
      employees: [
        {
          id: 'emp-001',
          name: 'Ms. Jessica Brown',
          employeeId: 'EMP-2021-03',
          position: 'Counselor',
          department: 'Mental Health Services',
          startDate: '2021-03-15',
          endDate: null,
          status: 'active'
        }
      ]
    };

    this.archivedRecords = {
      appointments: [
        {
          id: 'apt-arch-001',
          student: 'Student01',
          studentId: '2023-00001',
          college: 'CASS',
          program: 'Bachelor of Arts in Communication',
          date: '2025-06-01',
          time: '10:00 AM',
          counselor: 'Ms. Rivera',
          reason: 'Follow-up',
          status: 'archived',
          archivedDate: '2025-06-02'
        },
        {
          id: 'apt-arch-002',
          student: 'Student02',
          studentId: '2023-00002',
          college: 'CET',
          program: 'Bachelor of Science in Computer Science',
          date: '2025-05-28',
          time: '2:00 PM',
          counselor: 'Dr. Martinez',
          reason: 'Academic Support',
          status: 'archived',
          archivedDate: '2025-05-29'
        }
      ],
      dass21: [
        {
          id: 'dass-arch-001',
          studentId: '2023-00001',
          dateCompleted: '2025-05-30',
          depression: 8,
          anxiety: 12,
          stress: 10,
          riskLevel: 'Moderate',
          status: 'archived',
          archivedDate: '2025-06-01'
        }
      ],
      employees: [
        {
          id: 'emp-arch-001',
          name: 'Dr. Sarah Wilson',
          employeeId: 'EMP-2020-01',
          position: 'Senior Counselor',
          department: 'Student Services',
          startDate: '2020-01-15',
          endDate: '2025-04-30',
          status: 'archived',
          archivedDate: '2025-05-01'
        }
      ]
    };

    this.currentView = 'appointments';
    this.eventListeners = [];
    this.init();
  }

  init() {
    this.setupEventListeners();
    
    if (this.isArchivePage()) {
      this.renderCurrentView();
      this.showActiveRecordsNotification();
    }
    
    this.setupGlobalFunctions();
  }

  isArchivePage() {
    return document.getElementById('appointmentsArchive') !== null ||
           document.getElementById('dass21Archive') !== null ||
           document.getElementById('employeesArchive') !== null;
  }

  setupEventListeners() {
    // Clear existing listeners
    this.eventListeners.forEach(listener => {
      listener.element.removeEventListener(listener.event, listener.handler);
    });
    this.eventListeners = [];

    // Archive button listeners
    document.querySelectorAll('.archive-btn').forEach(btn => {
      const handler = (e) => {
        const type = e.currentTarget.getAttribute('data-type');
        if (type) {
          this.switchView(type);
        }
      };
      btn.addEventListener('click', handler);
      this.eventListeners.push({ element: btn, event: 'click', handler });
    });

    // Filter button listeners
    document.querySelectorAll('.filter-btn').forEach(btn => {
      const handler = () => this.showFilterOptions();
      btn.addEventListener('click', handler);
      this.eventListeners.push({ element: btn, event: 'click', handler });
    });

    // Export button listeners
    document.querySelectorAll('.export-btn').forEach(btn => {
      const handler = () => this.exportData();
      btn.addEventListener('click', handler);
      this.eventListeners.push({ element: btn, event: 'click', handler });
    });
  }

  setupGlobalFunctions() {
    // Make sure these functions are available globally
    window.archiveAppointment = (appointmentId) => {
      return this.archiveRecord('appointments', appointmentId);
    };
    
    window.showArchiveModal = (type, data) => {
      if (typeof data === 'string') {
        this.showArchiveModal(type, data);
      } else {
        this.showLegacyModal(type, data);
      }
    };
    
    window.closeArchiveModal = () => {
      this.closeModal();
    };

    // Expose archive manager globally
    window.archiveManager = this;
  }

  // Get appointment by ID - helper function
  getAppointmentById(appointmentId) {
    return this.activeRecords.appointments.find(apt => apt.id === appointmentId);
  }

  // Archive a record by moving it from active to archived
  archiveRecord(type, recordId) {
    console.log(`Attempting to archive ${type} record: ${recordId}`);
    
    const activeRecords = this.activeRecords[type];
    const recordIndex = activeRecords.findIndex(record => record.id === recordId);
    
    if (recordIndex !== -1) {
      const recordToArchive = { ...activeRecords[recordIndex] }; // Create a copy
      recordToArchive.status = 'archived';
      recordToArchive.archivedDate = new Date().toISOString().split('T')[0];
      
      // Move to archived records
      this.archivedRecords[type].push(recordToArchive);
      
      // Remove from active records
      this.activeRecords[type].splice(recordIndex, 1);
      
      // Show confirmation
      this.showNotification(`${this.capitalizeFirst(type.slice(0, -1))} archived successfully!`, 'success');
      
      // Refresh calendar if it exists
      this.refreshCalendar();
      
      // Refresh views if on archive page
      if (this.isArchivePage()) {
        this.renderCurrentView();
      }
      
      console.log(`Successfully archived ${type} record: ${recordId}`);
      return true;
    } else {
      console.log(`Record not found: ${recordId}`);
      this.showNotification(`Record not found: ${recordId}`, 'error');
    }
    
    return false;
  }

  // Restore a record by moving it from archived to active
  restoreRecord(type, recordId) {
    console.log(`Attempting to restore ${type} record: ${recordId}`);
    
    const archivedRecords = this.archivedRecords[type];
    const recordIndex = archivedRecords.findIndex(record => record.id === recordId);
    
    if (recordIndex !== -1) {
      const recordToRestore = { ...archivedRecords[recordIndex] }; // Create a copy
      recordToRestore.status = 'active';
      delete recordToRestore.archivedDate;
      
      // Move to active records
      this.activeRecords[type].push(recordToRestore);
      
      // Remove from archived records
      this.archivedRecords[type].splice(recordIndex, 1);
      
      // Show confirmation
      this.showNotification(`${this.capitalizeFirst(type.slice(0, -1))} restored successfully!`, 'success');
      
      // Refresh calendar if it exists
      this.refreshCalendar();
      
      // Refresh views
      if (this.isArchivePage()) {
        this.renderCurrentView();
      }
      
      console.log(`Successfully restored ${type} record: ${recordId}`);
      return true;
    } else {
      console.log(`Archived record not found: ${recordId}`);
      this.showNotification(`Archived record not found: ${recordId}`, 'error');
    }
    
    return false;
  }

  // Refresh calendar if it exists
  refreshCalendar() {
    if (window.calendar) {
      console.log('Refreshing calendar...');
      
      // Helper function to convert 12-hour time to 24-hour format
      const convertTo24Hour = (time12h) => {
        if (!time12h) return '00:00:00';
        const [time, modifier] = time12h.split(' ');
        let [hours, minutes] = time.split(':');
        
        if (hours === '12') hours = '00';
        if (modifier === 'PM') hours = parseInt(hours, 10) + 12;
        
        return `${hours}:${minutes}:00`;
      };

      // Update calendar events
      const calendarEvents = this.activeRecords.appointments.map(apt => ({
        id: apt.id,
        title: `${apt.student} - ${apt.reason}`,
        start: `${apt.date}T${convertTo24Hour(apt.time)}`,
        extendedProps: {
          studentId: apt.studentId,
          studentName: apt.student,
          college: apt.college,
          program: apt.program,
          counselor: apt.counselor,
          reason: apt.reason
        }
      }));

      // Remove all existing events
      window.calendar.removeAllEvents();
      
      // Add updated events
      window.calendar.addEventSource(calendarEvents);
      
      console.log(`Calendar refreshed with ${calendarEvents.length} events`);
    } else {
      console.log('Calendar not found - skipping refresh');
    }
  }

  // Switch between different archive views
  switchView(viewType) {
    this.currentView = viewType;
    
    // Update active button
    document.querySelectorAll('.archive-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    
    const activeBtn = document.querySelector(`[data-type="${viewType}"]`);
    if (activeBtn) {
      activeBtn.classList.add('active');
    }
    
    this.renderCurrentView();
  }

  // Render the current view
  renderCurrentView() {
    const container = document.getElementById(`${this.currentView}Archive`);
    if (!container) return;
    
    const records = this.archivedRecords[this.currentView];
    
    if (records.length === 0) {
      container.innerHTML = '<div class="no-data">No archived records found</div>';
      return;
    }
    
    let html = '';
    
    switch (this.currentView) {
      case 'appointments':
        html = this.renderAppointments(records);
        break;
      case 'dass21':
        html = this.renderDASS21(records);
        break;
      case 'employees':
        html = this.renderEmployees(records);
        break;
    }
    
    container.innerHTML = html;
  }

  renderAppointments(appointments) {
    return appointments.map(apt => `
      <div class="archive-item">
        <div class="archive-item-header">
          <h4>${apt.student}</h4>
          <span class="archive-date">Archived: ${apt.archivedDate}</span>
        </div>
        <div class="archive-item-details">
          <p><strong>Student ID:</strong> ${apt.studentId}</p>
          <p><strong>College:</strong> ${apt.college}</p>
          <p><strong>Program:</strong> ${apt.program}</p>
          <p><strong>Date:</strong> ${apt.date}</p>
          <p><strong>Time:</strong> ${apt.time}</p>
          <p><strong>Counselor:</strong> ${apt.counselor}</p>
          <p><strong>Reason:</strong> ${apt.reason}</p>
        </div>
        <div class="archive-item-actions">
          <button onclick="window.archiveManager.restoreRecord('appointments', '${apt.id}')" class="restore-btn">
            Restore
          </button>
          <button onclick="window.archiveManager.deleteRecord('appointments', '${apt.id}')" class="delete-btn">
            Delete Permanently
          </button>
        </div>
      </div>
    `).join('');
  }

  renderDASS21(records) {
    return records.map(record => `
      <div class="archive-item">
        <div class="archive-item-header">
          <h4>DASS-21 Assessment</h4>
          <span class="archive-date">Archived: ${record.archivedDate}</span>
        </div>
        <div class="archive-item-details">
          <p><strong>Student ID:</strong> ${record.studentId}</p>
          <p><strong>Date Completed:</strong> ${record.dateCompleted}</p>
          <p><strong>Depression:</strong> ${record.depression}</p>
          <p><strong>Anxiety:</strong> ${record.anxiety}</p>
          <p><strong>Stress:</strong> ${record.stress}</p>
          <p><strong>Risk Level:</strong> <span class="risk-level ${record.riskLevel.toLowerCase()}">${record.riskLevel}</span></p>
        </div>
        <div class="archive-item-actions">
          <button onclick="window.archiveManager.restoreRecord('dass21', '${record.id}')" class="restore-btn">
            Restore
          </button>
          <button onclick="window.archiveManager.deleteRecord('dass21', '${record.id}')" class="delete-btn">
            Delete Permanently
          </button>
        </div>
      </div>
    `).join('');
  }

  renderEmployees(employees) {
    return employees.map(emp => `
      <div class="archive-item">
        <div class="archive-item-header">
          <h4>${emp.name}</h4>
          <span class="archive-date">Archived: ${emp.archivedDate}</span>
        </div>
        <div class="archive-item-details">
          <p><strong>Employee ID:</strong> ${emp.employeeId}</p>
          <p><strong>Position:</strong> ${emp.position}</p>
          <p><strong>Department:</strong> ${emp.department}</p>
          <p><strong>Start Date:</strong> ${emp.startDate}</p>
          <p><strong>End Date:</strong> ${emp.endDate || 'N/A'}</p>
        </div>
        <div class="archive-item-actions">
          <button onclick="window.archiveManager.restoreRecord('employees', '${emp.id}')" class="restore-btn">
            Restore
          </button>
          <button onclick="window.archiveManager.deleteRecord('employees', '${emp.id}')" class="delete-btn">
            Delete Permanently
          </button>
        </div>
      </div>
    `).join('');
  }

  // Permanently delete a record
  deleteRecord(type, recordId) {
    if (confirm('Are you sure you want to permanently delete this record? This action cannot be undone.')) {
      const archivedRecords = this.archivedRecords[type];
      const recordIndex = archivedRecords.findIndex(record => record.id === recordId);
      
      if (recordIndex !== -1) {
        archivedRecords.splice(recordIndex, 1);
        this.showNotification(`${this.capitalizeFirst(type.slice(0, -1))} deleted permanently!`, 'success');
        this.renderCurrentView();
        return true;
      } else {
        this.showNotification(`Record not found: ${recordId}`, 'error');
      }
    }
    return false;
  }

  // Helper function to capitalize first letter
  capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // Show notification with better styling
  showNotification(message, type = 'info') {
    // Remove existing notifications
    document.querySelectorAll('.notification').forEach(notif => notif.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
      </div>
    `;
    
    // Add styles if they don't exist
    if (!document.getElementById('notification-styles')) {
      const style = document.createElement('style');
      style.id = 'notification-styles';
      style.textContent = `
        .notification {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 10000;
          padding: 15px 20px;
          border-radius: 8px;
          color: white;
          font-weight: 500;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          animation: slideIn 0.3s ease-out;
          max-width: 400px;
        }
        .notification.success {
          background-color: #10b981;
        }
        .notification.error {
          background-color: #ef4444;
        }
        .notification.info {
          background-color: #3b82f6;
        }
        .notification-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
        }
        .notification-close {
          background: none;
          border: none;
          color: white;
          font-size: 18px;
          cursor: pointer;
          padding: 0;
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `;
      document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }

  // Show active records notification
  showActiveRecordsNotification() {
    const totalActive = Object.values(this.activeRecords).reduce((sum, records) => sum + records.length, 0);
    if (totalActive > 0) {
      this.showNotification(`${totalActive} active records available for archiving`, 'info');
    }
  }

  // Filter functionality
  showFilterOptions() {
    alert('Filter options would be implemented here. You can filter by date range, status, counselor, etc.');
  }

  // Export functionality
  exportData() {
    const data = this.archivedRecords[this.currentView];
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `archived_${this.currentView}_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    this.showNotification(`Exported ${data.length} ${this.currentView} records`, 'success');
  }

  // Auto-archive old records (simulation)
  startAutoArchive() {
    setInterval(() => {
      this.autoArchiveOldRecords();
    }, 60000); // Check every minute
  }

  autoArchiveOldRecords() {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 30); // Archive records older than 30 days
    
    let archivedCount = 0;
    
    Object.keys(this.activeRecords).forEach(type => {
      const records = this.activeRecords[type];
      const oldRecords = records.filter(record => {
        const recordDate = new Date(record.date || record.dateCompleted || record.startDate);
        return recordDate < cutoffDate;
      });
      
      oldRecords.forEach(record => {
        if (this.archiveRecord(type, record.id)) {
          archivedCount++;
        }
      });
    });
    
    if (archivedCount > 0) {
      this.showNotification(`Auto-archived ${archivedCount} old records`, 'info');
    }
  }

  // Modal functions (for legacy compatibility)
  showArchiveModal(type, recordId) {
    console.log(`Showing archive modal for ${type}: ${recordId}`);
    // Implementation for showing archive modal would go here
  }

  showLegacyModal(type, data) {
    console.log(`Showing legacy modal for ${type}:`, data);
    // Implementation for legacy modal would go here
  }

  closeModal() {
    const modal = document.getElementById('archive-modal');
    if (modal) {
      modal.style.display = 'none';
    }
  }

  // Get statistics
  getStats() {
    const stats = {
      active: {},
      archived: {},
      total: {}
    };
    
    Object.keys(this.activeRecords).forEach(type => {
      stats.active[type] = this.activeRecords[type].length;
      stats.archived[type] = this.archivedRecords[type].length;
      stats.total[type] = stats.active[type] + stats.archived[type];
    });
    
    return stats;
  }

  // Debug function
  debugInfo() {
    console.log('Archive Manager Debug Info:');
    console.log('Active Records:', this.activeRecords);
    console.log('Archived Records:', this.archivedRecords);
    console.log('Stats:', this.getStats());
    console.log('Current View:', this.currentView);
  }
}

// Initialize archive manager
let archiveManager;

document.addEventListener('DOMContentLoaded', function() {
  console.log('Initializing Archive Manager...');
  
  archiveManager = new ArchiveManager();
  window.archiveManager = archiveManager;
  
  // Start auto-archive functionality
  archiveManager.startAutoArchive();
  
  // Global modal click handler
  window.addEventListener('click', function(e) {
    const modal = document.getElementById('archive-modal');
    if (e.target === modal) {
      archiveManager.closeModal();
    }
  });
  
  console.log('Archive Manager initialized successfully');
  
  // Debug info (remove in production)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.debugArchive = () => archiveManager.debugInfo();
    console.log('Debug function available: debugArchive()');
  }
});