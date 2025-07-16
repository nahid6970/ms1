// Example JavaScript -  A simple alert and a hover effect

document.addEventListener('DOMContentLoaded', function() {
    const alertButton = document.getElementById('alertButton');

    alertButton.addEventListener('click', function() {
        alert('Hello from JavaScript!');
    });

    const featureDivs = document.querySelectorAll('.feature');

    featureDivs.forEach(featureDiv => {
        featureDiv.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#ddd';
        });

        featureDiv.addEventListener('mouseout', function() {
            this.style.backgroundColor = '';
        });
    });
});