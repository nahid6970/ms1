function toggleFolder(folder) {
  const isExpanded = folder.classList.contains("expanded");

  // Collapse any other expanded folder
  document.querySelectorAll(".folder-container.expanded").forEach(expandedFolder => {
      if (expandedFolder !== folder) expandedFolder.classList.remove("expanded");
      expandedFolder.querySelectorAll(".icon.hidden").forEach(icon => icon.style.display = "none");
  });

  // Toggle the clicked folder
  folder.classList.toggle("expanded");

  // Show or hide hidden icons based on the expanded state
  folder.querySelectorAll(".icon.hidden").forEach(icon => {
      icon.style.display = folder.classList.contains("expanded") ? "inline-flex" : "none";
  });
}

// Close any expanded folder when clicking outside
window.onclick = function(event) {
  if (!event.target.closest(".folder-container")) {
      document.querySelectorAll(".folder-container.expanded").forEach(expandedFolder => {
          expandedFolder.classList.remove("expanded");
          expandedFolder.querySelectorAll(".icon.hidden").forEach(icon => icon.style.display = "none");
      });
  }
};