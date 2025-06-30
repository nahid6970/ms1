
document.addEventListener('DOMContentLoaded', () => {
    const modelSelector = document.getElementById('model-selector');
    const promptInput = document.getElementById('prompt-input');
    const sendButton = document.getElementById('send-button');
    const chatWindow = document.getElementById('chat-window');

    let messages = [];

    // Fetch models
    fetch('/api/models')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching models:', data.error);
                return;
            }
            data.forEach(model => {
                const option = document.createElement('option');
                option.value = model.name;
                option.textContent = model.name;
                modelSelector.appendChild(option);
            });
        });

    const sendMessage = () => {
        const prompt = promptInput.value;
        if (!prompt) return;

        const selectedModel = modelSelector.value;
        appendMessage('user', prompt);
        messages.push({ role: 'user', content: prompt });
        promptInput.value = '';

        const eventSource = new EventSource(`/chat?model=${selectedModel}&messages=${JSON.stringify(messages)}`);

        let assistantResponse = '';
        const assistantMessageElement = appendMessage('assistant', '');


        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.error) {
                assistantResponse += `\nError: ${data.error}`;
                assistantMessageElement.textContent = assistantResponse;
                eventSource.close();
                return;
            }
            assistantResponse += data.message.content;
            assistantMessageElement.textContent = assistantResponse;
            chatWindow.scrollTop = chatWindow.scrollHeight;
        };

        eventSource.onerror = (err) => {
            console.error('EventSource failed:', err);
            eventSource.close();
        };
    };

    const appendMessage = (role, content) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${role}-message`);
        messageElement.textContent = content;
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return messageElement;
    };

    sendButton.addEventListener('click', sendMessage);
    promptInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
