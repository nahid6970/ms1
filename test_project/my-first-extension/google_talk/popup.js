document.addEventListener('DOMContentLoaded', () => {
    const statusEl = document.getElementById('status');
    const wrapper = document.querySelector('.mic-wrapper');
    const btnEn = document.getElementById('btn-en');
    const btnBn = document.getElementById('btn-bn');

    let currentLang = 'en-US';
    let recognition = null;
    let isListening = false;
    let ignoreEndEvent = false;

    // Initialize logic
    chrome.storage.local.get(['speech_lang'], (result) => {
        if (result.speech_lang) {
            currentLang = result.speech_lang;
        }
        updateLangUI(currentLang);
        // Start automatically on open, small delay to ensure UI is ready
        setTimeout(startListening, 100);
    });

    function updateLangUI(lang) {
        if (lang === 'bn-BD') {
            btnBn.classList.add('active');
            btnEn.classList.remove('active');
        } else {
            btnEn.classList.add('active');
            btnBn.classList.remove('active');
        }
    }

    function switchLang(lang) {
        if (currentLang === lang) return;
        currentLang = lang;
        updateLangUI(lang);
        chrome.storage.local.set({ speech_lang: lang });

        // Restart recognition with new language
        if (isListening) {
            ignoreEndEvent = true; // Prevent default onend behavior if necessary
            if (recognition) recognition.stop();
        }
        // Small delay to allow stop to process
        setTimeout(() => {
            ignoreEndEvent = false;
            startListening();
        }, 300);
    }

    btnEn.addEventListener('click', () => switchLang('en-US'));
    btnBn.addEventListener('click', () => switchLang('bn-BD'));

    function startListening() {
        if (isListening) return;

        if (!('webkitSpeechRecognition' in window)) {
            statusEl.textContent = "Not Supported";
            return;
        }

        try {
            recognition = new webkitSpeechRecognition();
            recognition.lang = currentLang;
            recognition.continuous = false;
            recognition.interimResults = true;

            recognition.onstart = () => {
                isListening = true;
                wrapper.classList.add('listening');
                statusEl.textContent = ''; // Clear status on start
            };

            recognition.onend = () => {
                isListening = false;
                wrapper.classList.remove('listening');
                if (!ignoreEndEvent) {
                     // If we didn't explicitly stop to switch lang, maybe show ready state?
                     // Keeping it clean as requested.
                }
            };

            recognition.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                isListening = false;
                wrapper.classList.remove('listening');
                if (event.error === 'not-allowed') {
                    statusEl.textContent = "Allow Microphone";
                } else if (event.error === 'no-speech') {
                    // statusEl.textContent = "No speech detected"; // Optional: keep silent or subtle
                } else {
                    statusEl.textContent = "Error: " + event.error;
                }
            };

            recognition.onresult = (event) => {
                let finalTranscript = '';
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                if (finalTranscript.length > 0) {
                    performSearch(finalTranscript);
                } else if (interimTranscript.length > 0) {
                    statusEl.textContent = interimTranscript;
                }
            };

            recognition.start();
        } catch (e) {
            console.error(e);
            statusEl.textContent = "Error starting";
        }
    }

    function performSearch(queryText) {
        // Optional feedback before redirect
        // statusEl.textContent = "Searching..."; 
        if (recognition) recognition.stop();

        const query = encodeURIComponent(queryText);
        const url = `https://www.google.com/search?q=${query}`;

        chrome.tabs.create({ url: url });
    }

    // Toggle listening on click
    wrapper.addEventListener('click', () => {
        if (isListening) {
            if (recognition) recognition.stop();
        } else {
            startListening();
        }
    });
});