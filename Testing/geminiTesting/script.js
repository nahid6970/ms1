document.addEventListener('DOMContentLoaded', function() {
    const dataStream = document.querySelector('.data-stream');
    const messages = [
        '> ANALYZING SYSTEM...',
        '> KERNEL INTEGRITY: 100%',
        '> FIREWALL STATUS: ACTIVE',
        '> DECRYPTION PROTOCOLS ENGAGED.',
        '> BOOTING SENTINEL PROGRAM...',
        { text: '> ACCESSING MAINFRAME... [ACCESS GRANTED]', className: 'success' },
        '> RUNNING DIAGNOSTICS...',
        { text: '> WARNING: UNKNOWN SIGNATURE DETECTED IN GRID 4.', className: 'error' },
        '> ISOLATING ANOMALY...',
        '> REROUTING POWER...',
        '> GRID 4 SECURED.',
        '> ALL SYSTEMS NOMINAL.'
    ];

    let messageIndex = 0;

    function typeMessage() {
        if (messageIndex < messages.length) {
            const p = document.createElement('p');
            const message = messages[messageIndex];
            
            if (typeof message === 'object') {
                p.textContent = message.text;
                if(message.className) {
                    p.classList.add(message.className);
                }
            } else {
                p.textContent = message;
            }

            dataStream.appendChild(p);
            dataStream.scrollTop = dataStream.scrollHeight; // Auto-scroll to bottom
            messageIndex++;

            setTimeout(typeMessage, Math.random() * 2000 + 500); // Random delay for next message
        }
    }

    // Clear existing messages and start typing
    const existingMessages = dataStream.querySelectorAll('p');
    existingMessages.forEach(msg => msg.remove());
    setTimeout(typeMessage, 1000);

function add(a, b) {
    return a + b;
}

// Test case for add function
function testAdd() {
    console.assert(add(2, 3) === 5, "add(2, 3) should return 5");
    console.assert(add(-1, 1) === 0, "add(-1, 1) should return 0");
    console.assert(add(0, 0) === 0, "add(0, 0) should return 0");
    console.log("All add tests passed!");
}

// Run tests
testAdd();
