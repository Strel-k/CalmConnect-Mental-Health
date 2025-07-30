/*window.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("userMeta")) {
    document.getElementById("introForm").style.display = "none";
  }
}); */

document.getElementById("userInfoForm").addEventListener("submit", function (e) {
  e.preventDefault();

  // Optionally store user data in localStorage or pass to backend
  const formData = new FormData(this);
  const userData = Object.fromEntries(formData.entries());

  console.log("User Data Collected:", userData); // for now, just log

  // Hide the form overlay
  document.getElementById("introForm").style.display = "none";

  // Optionally store in localStorage for session use
  localStorage.setItem("userMeta", JSON.stringify(userData));
});