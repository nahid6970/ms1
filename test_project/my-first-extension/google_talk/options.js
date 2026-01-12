document.addEventListener('DOMContentLoaded', () => {
    const langSelect = document.getElementById('lang');
    const saveBtn = document.getElementById('save');
    const toast = document.getElementById('toast');

    // Load saved settings
    chrome.storage.local.get(['speech_lang'], (result) => {
        if (result.speech_lang) {
            langSelect.value = result.speech_lang;
        }
    });

    saveBtn.addEventListener('click', () => {
        const selectedLang = langSelect.value;
        chrome.storage.local.set({ speech_lang: selectedLang }, () => {
            // Show toast
            toast.style.opacity = '1';
            setTimeout(() => {
                toast.style.opacity = '0';
            }, 2000);
        });
    });
});
