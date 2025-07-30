let editTargetRow = null;

function openAddModal() {
  document.getElementById("modal-title").textContent = "Add Counselor";
  document.getElementById("personnel-form").reset();
  document.getElementById("photoPreview").src = "img/default.jpg";
  editTargetRow = null;
  document.getElementById("personnel-modal").classList.add("show");

}

function openEditModal(button) {
  const row = button.closest("tr");
  const cells = row.querySelectorAll("td");

  const photoSrc = cells[0].querySelector("img").src;
  const name = cells[1].textContent;
  const email = cells[2].textContent;
  const unit = cells[3].textContent;
  const rank = cells[4].textContent;

  document.getElementById("modal-title").textContent = "Edit Counselor";
  document.getElementById("photoPreview").src = photoSrc;
  document.getElementById("nameInput").value = name;
  document.getElementById("emailInput").value = email;
  document.getElementById("unitInput").value = unit;
  document.getElementById("rankInput").value = rank;

  document.getElementById("personnel-modal").style.display = "block";
}



function closeModal() {
  document.getElementById("personnel-modal").style.display = "none";
  editTargetRow = null;
}

function previewPhoto() {
  const file = document.getElementById("photoInput").files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      document.getElementById("photoPreview").src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
}

document.getElementById("personnel-form").addEventListener("submit", function (e) {
  e.preventDefault();

  const name = document.getElementById("nameInput").value;
  const email = document.getElementById("emailInput").value;
  const unit = document.getElementById("unitInput").value;
  const rank = document.getElementById("rankInput").value;
  const photo = document.getElementById("photoPreview").src;

  const newRow = document.createElement("tr");
  newRow.innerHTML = `
    <td><img src="${photo}" class="counselor-photo" alt="${name}" /></td>
    <td>${name}</td>
    <td>${email}</td>
    <td>${unit}</td>
    <td>${rank}</td>
    <td>
      <button onclick="openEditModal(this)">Edit</button>
      <button onclick="archiveCounselor('${name}')">Archive</button>
    </td>
  `;

  document.getElementById("counselor-list").appendChild(newRow);
  closeModal();
  this.reset();
  document.getElementById("photoPreview").src = "img/default.jpg";
});


function archiveCounselor(name) {
  if (confirm(`Archive counselor ${name}?`)) {
    const rows = document.querySelectorAll("#counselor-list tr");
    rows.forEach(row => {
      if (row.innerText.includes(name)) row.remove();
    });
  }
}

// Optional: close modal by clicking outside
window.onclick = function (e) {
  const modal = document.getElementById("personnel-modal");
  if (e.target === modal) closeModal();
};
