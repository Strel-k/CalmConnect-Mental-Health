document.addEventListener("DOMContentLoaded", () => {
    // Select elements by their actual classes/structure in your HTML
    const profileImg = document.querySelector(".prfl-container img");
    const bellIcon = document.querySelector(".bx.bxs-bell");
    
    // Create dropdown elements dynamically if they don't exist
    let profileDropdown = document.getElementById("profile-dropdown");
    let bellDropdown = document.getElementById("bell-dropdown");
    
    if (!profileDropdown) {
        profileDropdown = document.createElement("div");
        profileDropdown.id = "profile-dropdown";
        profileDropdown.className = "dropdown";
        profileDropdown.style.display = "none";
        profileDropdown.innerHTML = `
            <div class="dropdown-item">Profile Settings</div>
            <div class="dropdown-item">Account</div>
            <div class="dropdown-item">Logout</div>
        `;
        document.querySelector(".prfl-container").appendChild(profileDropdown);
    }
    
    if (!bellDropdown) {
        bellDropdown = document.createElement("div");
        bellDropdown.id = "bell-dropdown";
        bellDropdown.className = "dropdown";
        bellDropdown.style.display = "none";
        bellDropdown.innerHTML = `
            <div class="dropdown-item">New appointment scheduled</div>
            <div class="dropdown-item">High-risk case flagged</div>
            <div class="dropdown-item">Assessment completed</div>
        `;
        document.querySelector(".prfl-bell").appendChild(bellDropdown);
    }
  
    // Toggle profile dropdown
    if (profileImg) {
        profileImg.addEventListener("click", (e) => {
            profileDropdown.style.display = profileDropdown.style.display === "flex" ? "none" : "flex";
            bellDropdown.style.display = "none"; // close other dropdown
            e.stopPropagation();
        });
    }
  
    // Toggle bell dropdown
    if (bellIcon) {
        bellIcon.addEventListener("click", (e) => {
            bellDropdown.style.display = bellDropdown.style.display === "flex" ? "none" : "flex";
            profileDropdown.style.display = "none"; // close other dropdown
            e.stopPropagation();
        });
    }
  
    // Close both dropdowns when clicking outside
    document.addEventListener("click", () => {
        if (profileDropdown) profileDropdown.style.display = "none";
        if (bellDropdown) bellDropdown.style.display = "none";
    });
});