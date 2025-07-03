    // Function to add copy icons and handle copying
    function addCopyIcons() {
      const listItems = document.querySelectorAll('#list li');

      listItems.forEach(li => {
        // Create the copy icon
        const copyIcon = document.createElement('span');
        copyIcon.innerHTML = '📋'; // You can use any icon or SVG here
        copyIcon.className = 'copy-icon';

        // Add the copy functionality
        copyIcon.addEventListener('click', () => {
          const textToCopy = li.textContent.trim();
          navigator.clipboard.writeText(textToCopy).then(() => {
            alert(`Copied: "${textToCopy}"`);
          }).catch(err => {
            console.error('Failed to copy text: ', err);
          });
        });

        // Append the icon to the list item
        li.appendChild(copyIcon);
      });
    }

    // Run the function when the page loads
    document.addEventListener('DOMContentLoaded', addCopyIcons);