(function() {
  document.addEventListener('change', function(e) {
    if (e.target && e.target.type === 'checkbox' && e.target.checked) {
      let chs = document.querySelectorAll('.checkboxColumn input[type="checkbox"]');
      
      // Fallback to all visible checkboxes if .checkboxColumn is not found
      if (chs.length === 0) {
        chs = Array.from(document.querySelectorAll('input[type="checkbox"]')).filter(el => {
          return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
        });
      }
      
      for (let i = 0; i < chs.length; i++) {
        if (!chs[i].checked) {
          chs[i].checked = true;
          chs[i].dispatchEvent(new Event('change', { bubbles: true }));
        }
      }
    }
  });
  console.log('Checkbox Auto Checker script loaded.');
})();
