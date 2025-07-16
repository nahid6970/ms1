// Example:  Add a simple hover effect to the project images
const projects = document.querySelectorAll('.project img');

projects.forEach(project => {
  project.addEventListener('mouseover', () => {
    project.style.opacity = '0.8';
  });

  project.addEventListener('mouseout', () => {
    project.style.opacity = '1';
  });
});