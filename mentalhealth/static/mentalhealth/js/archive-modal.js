let currentReportData = null;
let currentReportType = null;

function showArchiveModal(type, data) {
  const modal = document.getElementById("archive-modal");
  const body = document.getElementById("modal-body");
  const title = document.getElementById("modal-title");

  currentReportData = data;
  currentReportType = type;

  title.textContent = `${type.charAt(0).toUpperCase() + type.slice(1)} Report`;

  let content = "";

  if (type === "appointments") {
    content = `
      <p><strong>Student:</strong> ${data.student}</p>
      <p><strong>Date:</strong> ${data.date}</p>
      <p><strong>Time:</strong> ${data.time || "10:00 AM"}</p>
      <p><strong>Counselor:</strong> ${data.counselor}</p>
      <p><strong>Reason for Visit:</strong> ${data.reason}</p>
      <p><strong>Status:</strong> Completed</p>
      <p><strong>Notes:</strong> This session focused on follow-up and evaluation.</p>
    `;
  } else if (type === "dass21") {
    content = `
      <p><strong>Student:</strong> ${data.user}</p>
      <p><strong>Date:</strong> ${data.date}</p>
      <p><strong>Anxiety Score:</strong> ${data.anxiety}</p>
      <p><strong>Depression Score:</strong> ${data.depression}</p>
      <p><strong>Stress Score:</strong> ${data.stress}</p>
      <p><strong>Remarks:</strong> ${data.remarks}</p>
    `;
  } else if (type === "employee") {
    content = `
      <p><strong>Username:</strong> ${data.username}</p>
      <p><strong>Name:</strong> ${data.name}</p>
      <p><strong>Email:</strong> ${data.email}</p>
      <p><strong>Role:</strong> ${data.role}</p>
      <p><strong>Unit:</strong> ${data.unit}</p>
      <p><strong>Rank:</strong> ${data.rank}</p>
    `;
  }

  body.innerHTML = content;
  modal.style.display = "block";
}




  function closeArchiveModal() {
    document.getElementById("archive-modal").style.display = "none";
  }

  // Optional: close modal by clicking outside
  window.onclick = function(e) {
    const modal = document.getElementById("archive-modal");
    if (e.target === modal) closeArchiveModal();
  };
  document.getElementById("downloadPdfBtn").addEventListener("click", function () {
  if (!currentReportData || !currentReportType) return;

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  doc.setFontSize(16);
  doc.text(`${currentReportType.charAt(0).toUpperCase() + currentReportType.slice(1)} Report`, 20, 20);
  doc.setFontSize(12);

  let y = 30;

  if (currentReportType === "appointments") {
    doc.text(`Student: ${currentReportData.student}`, 20, y); y += 10;
    doc.text(`Date: ${currentReportData.date}`, 20, y); y += 10;
    doc.text(`Time: ${currentReportData.time || "10:00 AM"}`, 20, y); y += 10;
    doc.text(`Counselor: ${currentReportData.counselor}`, 20, y); y += 10;
    doc.text(`Reason for Visit: ${currentReportData.reason}`, 20, y); y += 10;
    doc.text(`Status: Completed`, 20, y); y += 10;
    doc.text(`Notes: This session focused on follow-up and evaluation.`, 20, y);
  }
  else if (currentReportType === "employee") {
  doc.text(`Name: ${currentReportData.name}`, 20, y); y += 10;
  doc.text(`Email: ${currentReportData.email}`, 20, y); y += 10;
  doc.text(`Role: ${currentReportData.role}`, 20, y); y += 10;
  doc.text(`Unit: ${currentReportData.unit}`, 20, y); y += 10;
  doc.text(`Rank: ${currentReportData.rank}`, 20, y); y += 10;
}

  doc.save(`${currentReportType}-report.pdf`);
});
function showEmployeePDF(data) {
  const { username, firstName, lastName, email, role, unit, rank } = data;

  const doc = new jsPDF();
  doc.setFontSize(14);
  doc.setTextColor(40);
  doc.text("Archived Employee Report", 20, 20);

  doc.setFontSize(12);
  doc.text(`Username: ${username}`, 20, 40);
  doc.text(`Name: ${firstName} ${lastName}`, 20, 50);
  doc.text(`Email: ${email}`, 20, 60);
  doc.text(`Role: ${role}`, 20, 70);
  doc.text(`Unit: ${unit}`, 20, 80);
  doc.text(`Rank: ${rank}`, 20, 90);

  doc.save(`${username}_employee_report.pdf`);
}
