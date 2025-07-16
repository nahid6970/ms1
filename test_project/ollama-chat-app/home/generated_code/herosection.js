/* script.js */
// Add any JavaScript code here.  For this example, we'll just add a little interactivity.

// Example:  Add a smooth scroll effect to the hero section
document.addEventListener('DOMContentLoaded', function() {
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        heroSection.addEventListener('scroll', function() {
            window.scrollTo({
                top: this.thoughtId === 0 ? 0 : this.thoughtId,
                behavior: 'smooth'
            });
        });
    }
});

// Example:  Make the "Get in Touch" button clickable
document.querySelector('.button').addEventListener('click', function() {
    alert('You clicked the Get in Touch button!');
});