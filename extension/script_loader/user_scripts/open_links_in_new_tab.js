(function() {
  let domainWhitelist = '';
  
  // Load initial settings
  chrome.storage.local.get(['domainWhitelist'], (result) => {
    domainWhitelist = result.domainWhitelist || '';
  });

  // Listen for setting changes
  chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'local' && changes.domainWhitelist) {
      domainWhitelist = changes.domainWhitelist.newValue || '';
    }
  });

  function isWhitelisted() {
    const whitelist = domainWhitelist.trim();
    if (whitelist === '') return true; // Work everywhere if empty

    const currentHost = window.location.hostname.toLowerCase();
    const domains = whitelist.split(',').map(d => d.trim().toLowerCase()).filter(d => d !== '');
    
    return domains.some(domain => currentHost === domain || currentHost.endsWith('.' + domain));
  }

  // Use a capturing listener at the highest level to intercept the event early
  document.addEventListener('click', (event) => {
    // Only handle primary (left) clicks
    if (event.button !== 0) return;

    // Preserve default behavior for modifier keys (Ctrl, Shift, etc.)
    if (event.ctrlKey || event.shiftKey || event.altKey || event.metaKey) return;

    // Find the closest anchor tag
    const link = event.target.closest('a');

    // Basic validation for the link itself
    if (link && link.href && 
        !link.href.startsWith('javascript:') && 
        !link.getAttribute('href').startsWith('#') &&
        link.target !== '_blank') {
      
      // Check whitelist (synchronously using the cached value)
      if (isWhitelisted()) {
        // 1. Prevent default navigation
        event.preventDefault();
        
        // 2. Stop propagation to prevent other scripts from seeing this click
        // This helps prevent "click effects" or duplicate triggers
        event.stopPropagation();
        event.stopImmediatePropagation();
        
        // 3. Open in a new tab
        window.open(link.href, '_blank');
        
        console.log('Script: Opening link in new tab and suppressing effects (Whitelisted):', link.href);
      }
    }
  }, true); // TRUE for capture phase - intercept before it reaches the element
})();
