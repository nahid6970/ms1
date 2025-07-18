document.addEventListener('DOMContentLoaded', () => {
  const scriptListDiv = document.getElementById('scriptList');

  const allAvailableScripts = [
    'user_scripts/sample_script.js',
    'user_scripts/disable_youtube.js',
    'user_scripts/dark_mode_toggle.js',
    'user_scripts/text_highlighter.js',
    'user_scripts/youtube_ad_skipper.js',  // Added the YouTube ad skipper
    // Add more script paths here, e.g., 'user_scripts/my_new_script.js'
  ];

  if (allAvailableScripts.length > 0) {
    chrome.storage.local.get(['enabledScripts'], (result) => {
      const enabledScripts = result.enabledScripts || {};

      allAvailableScripts.forEach(scriptPath => {
        const fileName = scriptPath.split('/').pop(); // Get filename with extension
        const scriptName = fileName.replace('.js', ''); // Get filename without extension
        const scriptId = scriptPath.replace(/[^a-zA-Z0-9]/g, '_'); // Sanitize for ID

        const scriptItem = document.createElement('div');
        scriptItem.className = 'script-item';

        scriptItem.innerHTML = `
          <input type="checkbox" id="${scriptId}">
          <label for="${scriptId}">${scriptName}</label>
        `;

        const checkboxInput = scriptItem.querySelector(`#${scriptId}`);

        checkboxInput.checked = enabledScripts[scriptPath] || false;

        checkboxInput.addEventListener('change', () => {
          enabledScripts[scriptPath] = checkboxInput.checked;
          chrome.storage.local.set({ enabledScripts });
        });

        scriptListDiv.appendChild(scriptItem);
      });
    });
  } else {
    scriptListDiv.innerHTML = '<p>No scripts configured. Add script paths to popup.js.</p>';
  }
});