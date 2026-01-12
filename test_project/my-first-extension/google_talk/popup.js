document.addEventListener('DOMContentLoaded', () => {
    const statusEl = document.getElementById('status');
    const langDisplayEl = document.getElementById('lang-display');
    const wrapper = document.querySelector('.mic-wrapper');

    let currentLang = 'en-US';
    let recognition;
    let isListening = false;

    // Initialize logic
    chrome.storage.local.get(['speech_lang'], (result) => {
        if (result.speech_lang) {
            currentLang = result.speech_lang;
        }

        // Update UI text
        langDisplayEl.textContent = currentLang === 'bn-BD' ? 'Bangla' : 'English';

        // Start automatically on open
        startListening();
    });

    function startListening() {
        if (isListening) return;

        if (!('webkitSpeechRecognition' in window)) {
            statusEl.textContent = "Not Supported";
            return;
        }

        recognition = new webkitSpeechRecognition();
        recognition.lang = currentLang;
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onstart = () => {
            isListening = true;
            statusEl.textContent = currentLang === 'bn-BD' ? 'শোনা হচ্ছে...' : 'Listening...';
            wrapper.classList.add('listening');
        };

        recognition.onend = () => {
            isListening = false;
            wrapper.classList.remove('listening');
            // If the socket closed and we haven't searched yet, reset status
            if (statusEl.textContent.trim().length === 0 || statusEl.textContent === "Listening..." || statusEl.textContent === 'শোনা হচ্ছে...') {
                statusEl.textContent = "Tap to retry";
            }
        };

        recognition.onerror = (event) => {
            console.error(event.error);
            isListening = false;
            wrapper.classList.remove('listening');
            if (event.error === 'not-allowed') {
                statusEl.textContent = "Allow Microphone";
            } else {
                statusEl.textContent = "Error";
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
                // Final result - Search immediately
                performSearch(finalTranscript);
            } else if (interimTranscript.length > 0) {
                // Interim result - Show in UI
                statusEl.textContent = interimTranscript;
            }
        };

        try {
            recognition.start();
        } catch (e) {
            console.error(e);
            statusEl.textContent = "Error starting";
        }
    }

    function performSearch(queryText) {
        statusEl.textContent = "Searching...";
        recognition.stop(); // Ensure it stops

        const query = encodeURIComponent(queryText);
        const url = `https://www.google.com/search?q=${query}`;

        chrome.tabs.create({ url: url });
        // Optional: Close current popup
        // window.close();
    }

    // Allow clicking the mic to restart manually or stop (which triggers result finalization)
    wrapper.addEventListener('click', () => {
        if (!isListening) {
            startListening();
        } else {
            recognition.stop();
        }
    });

    // Allow clicking lang to go to options
    langDisplayEl.addEventListener('click', () => {
        chrome.runtime.openOptionsPage();
    });
});
