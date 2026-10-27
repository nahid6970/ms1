(function() {
  document.addEventListener('click', function(e) {
    if (e.ctrlKey || e.metaKey) {
      const link = e.target.closest('a');
      if (link) {
        e.preventDefault();
        e.stopPropagation();

        const text = link.innerText.trim();
        if (text) {
          navigator.clipboard.writeText(text).then(() => {
            showTooltip(e.clientX, e.clientY, `Copied: "${text.substring(0, 20)}${text.length > 20 ? '...' : ''}"`);
          }).catch(err => {
            console.error('Failed to copy link text:', err);
          });
        }
      }
    }
  }, true);

  function showTooltip(x, y, message) {
    const tooltip = document.createElement('div');
    tooltip.textContent = message;
    tooltip.style.position = 'fixed';
    tooltip.style.left = `${x + 10}px`;
    tooltip.style.top = `${y + 10}px`;
    tooltip.style.background = '#1e1e1e';
    tooltip.style.color = '#4ec9b0';
    tooltip.style.border = '1px solid #3c3c3c';
    tooltip.style.padding = '6px 12px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '11px';
    tooltip.style.fontFamily = "'JetBrains Mono', monospace";
    tooltip.style.zIndex = '100000';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.boxShadow = '0 4px 10px rgba(0,0,0,0.4)';
    tooltip.style.transition = 'opacity 0.2s ease';
    
    document.body.appendChild(tooltip);

    setTimeout(() => {
      tooltip.style.opacity = '0';
      setTimeout(() => {
        tooltip.remove();
      }, 200);
    }, 1500);
  }

  console.log('Link Text Extractor loaded.');
})();
