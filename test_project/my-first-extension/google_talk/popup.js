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
        recognition.interimResults = false;

        recognition.onstart = () => {
            isListening = true;
            statusEl.textContent = currentLang === 'bn-BD' ? 'শোনা হচ্ছে...' : 'Listening...';
            wrapper.classList.add('listening');
        };

        recognition.onend = () => {
            isListening = false;
            wrapper.classList.remove('listening');
            // If we closed without result, just revert status
            if (statusEl.textContent !== "Searching...") {
                 statusEl.textContent = "Tap to retry";
            }
        };

        recognition.onerror = (event) => {
            console.error(event.error);
            isListening = false;
            wrapper.classList.remove('listening');
            if(event.error === 'not-allowed') {
                 statusEl.textContent = "Allow Microphone";
            } else {
                 statusEl.textContent = "Error"; // Keep it simple
            }
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (transcript.trim().length > 0) {
                statusEl.textContent = "Searching...";
                
                // Perform Search
                const query = encodeURIComponent(transcript);
                const url = `https://www.google.com/search?q=${query}`;
                
                chrome.tabs.create({ url: url });
                
                // Optional: Close the popup after a slight delay
                // window.close(); 
            }
        };

        try {
            recognition.start();
        } catch(e) {
            console.error(e);
            statusEl.textContent = "Error starting";
        }
    }
    
    // Allow clicking the mic to restart manually
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
