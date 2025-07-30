
function exportToCSV() {
  const rows = [['User', 'Date', 'Anxiety', 'Depression', 'Stress']];
  document.querySelectorAll('.data-table tbody tr').forEach(tr => {
    const row = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
    rows.push(row);
  });

  let csvContent = rows.map(e => e.join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", "DASS21_data.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function exportToPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  doc.setFontSize(14);
  doc.text("DASS21 Test Data", 14, 20);

  const headers = [['User', 'Date', 'Anxiety', 'Depression', 'Stress']];
  const rows = [];

  document.querySelectorAll('.data-table tbody tr').forEach(tr => {
    const row = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
    rows.push(row);
  });

  doc.autoTable({
    head: headers,
    body: rows,
    startY: 30
  });

  doc.save("DASS21_data.pdf");
}
function exportChartAsImage(canvasId) {
  const canvas = document.getElementById(canvasId);
  const link = document.createElement('a');
  link.href = canvas.toDataURL('image/png');
  link.download = `${canvasId}.png`;
  link.click();
}

function exportChartAsPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  const canvas1 = document.getElementById('collegeChart');
  const canvas2 = document.getElementById('combinedCollegeChart');

  const img1 = canvas1.toDataURL('image/png');
  const img2 = canvas2.toDataURL('image/png');

  doc.text("College Chart", 10, 10);
  doc.addImage(img1, 'PNG', 10, 15, 180, 90);

  doc.addPage();
  doc.text("Combined Chart", 10, 10);
  doc.addImage(img2, 'PNG', 10, 15, 180, 90);

  doc.save("DASS21_Charts.pdf");
}
function exportToExcel() {
  const table = document.querySelector('.data-table');
  const workbook = XLSX.utils.table_to_book(table, { sheet: "DASS21 Data" });
  XLSX.writeFile(workbook, 'DASS21_data.xlsx');
}
