// Create a style element for the highlighter
const style = document.createElement('style');
style.textContent = `
  .highlight-overlay {
    position: absolute;
    background-color: rgba(0, 123, 255, 0.5);
    border: 2px solid #007bff;
    border-radius: 3px;
    z-index: 99999;
    pointer-events: none; /* So it doesn't interfere with clicks */
    transition: all 0.1s ease-in-out;
  }
`;
document.head.appendChild(style);

let ctrlPressed = false;
let highlightedElement = null;
let overlay = null;

// Create the overlay element
function createOverlay() {
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'highlight-overlay';
    document.body.appendChild(overlay);
  }
}

// Update overlay position and size
function updateOverlay(element) {
  if (element && overlay) {
    const rect = element.getBoundingClientRect();
    overlay.style.width = `${rect.width}px`;
    overlay.style.height = `${rect.height}px`;
    overlay.style.top = `${window.scrollY + rect.top}px`;
    overlay.style.left = `${window.scrollX + rect.left}px`;
    overlay.style.display = 'block';
  } else if (overlay) {
    overlay.style.display = 'none';
  }
}

// Mouseover handler
const handleMouseOver = (event) => {
  if (ctrlPressed) {
    highlightedElement = event.target;
    updateOverlay(highlightedElement);
  }
};

// Mouseout handler
const handleMouseOut = (event) => {
  if (highlightedElement) {
    highlightedElement = null;
    updateOverlay(null);
  }
};

// Keydown handler
window.addEventListener('keydown', (event) => {
  if (event.key === 'Control' && !ctrlPressed) {
    ctrlPressed = true;
    createOverlay();
    document.addEventListener('mouseover', handleMouseOver);
    document.addEventListener('mouseout', handleMouseOut);
  }
});

// Keyup handler
window.addEventListener('keyup', (event) => {
  if (event.key === 'Control') {
    ctrlPressed = false;
    highlightedElement = null;
    updateOverlay(null);
    document.removeEventListener('mouseover', handleMouseOver);
    document.removeEventListener('mouseout', handleMouseOut);
  }
});

// Mousedown handler for popping out the element
document.addEventListener('mousedown', (event) => {
  if (ctrlPressed && event.button === 0 && highlightedElement) {
    event.preventDefault();
    event.stopPropagation();

    const targetElement = highlightedElement;

    if (targetElement) {
      const rect = targetElement.getBoundingClientRect();
      const newWindow = window.open('', '', `width=${rect.width},height=${rect.height},left=${window.screenX + rect.left},top=${window.screenY + rect.top}`);
      
      if (newWindow) {
        // Copy all stylesheets from the original document
        const styleSheets = Array.from(document.styleSheets)
          .map(ss => {
            try {
              return Array.from(ss.cssRules || [])
                .map(rule => rule.cssText)
                .join('\n');
            } catch (e) {
              // For external stylesheets, you might not have access
              if (ss.href) {
                return `<link rel="stylesheet" href="${ss.href}">`;
              }
              return '';
            }
          })
          .join('\n');

        // Create a style element for the stylesheets
        const styleElement = newWindow.document.createElement('style');
        styleElement.textContent = styleSheets;
        
        // For linked stylesheets, create link elements
        const headContent = styleSheets.includes('<link') 
          ? styleSheets.match(/<link[^>]*>/g).join('') 
          : '';
        
        newWindow.document.head.innerHTML = headContent;
        newWindow.document.head.appendChild(styleElement);
        
        // Basic styling for the new window
        const newStyle = newWindow.document.createElement('style');
        newStyle.textContent = `
          body, html { margin: 0; padding: 0; overflow: hidden; }
          * { box-sizing: border-box; }
        `;
        newWindow.document.head.appendChild(newStyle);
        
        // Set the content
        newWindow.document.body.innerHTML = targetElement.outerHTML;
      }
    }
  }
}, true);