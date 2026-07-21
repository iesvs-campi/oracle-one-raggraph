const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const loading = document.getElementById('loading');

// Mantenemos el historial de la conversación para enviarlo al backend
let conversationHistory = [];

// Permitir enviar con la tecla Enter
userInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    // Añadir mensaje del usuario al chat visual
    appendMessage(query, 'user');
    
    // Añadir mensaje al historial
    conversationHistory.push({ role: "user", content: query });
    
    userInput.value = '';
    
    // Deshabilitar input mientras carga
    userInput.disabled = true;
    sendBtn.disabled = true;
    loading.style.display = 'block';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ messages: conversationHistory })
        });

        if (!response.ok) {
            throw new Error('Error en el servidor');
        }

        const data = await response.json();
        
        // Añadir la respuesta del bot al historial
        conversationHistory.push({ role: "bot", content: data.response });
        
        // Mostrar la respuesta visualmente
        appendMessage(data.response, 'bot', data.sources);

    } catch (error) {
        console.error(error);
        appendMessage('Lo siento, ocurrió un error al procesar tu solicitud. Inténtalo de nuevo más tarde.', 'bot');
        // Quitamos el mensaje del usuario del historial si falló
        conversationHistory.pop();
    } finally {
        // Rehabilitar input
        userInput.disabled = false;
        sendBtn.disabled = false;
        loading.style.display = 'none';
        userInput.focus();
    }
}

function appendMessage(text, sender, sources = []) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    // XSS PROTECTION: Usamos textContent en lugar de innerHTML.
    // CSS (white-space: pre-wrap) se encarga de renderizar los saltos de línea \n correctamente.
    // Esto asegura que cualquier etiqueta HTML maliciosa se muestre como texto plano.
    const textNodeDiv = document.createElement('div');
    textNodeDiv.textContent = text;
    messageDiv.appendChild(textNodeDiv);

    // Añadir fuentes si existen y es el bot
    if (sender === 'bot' && sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.classList.add('sources');
        sourcesDiv.textContent = 'Fuentes consultadas: ';
        
        sources.forEach(source => {
            const tag = document.createElement('span');
            tag.classList.add('source-tag');
            tag.textContent = source; // Protección XSS adicional para las fuentes
            sourcesDiv.appendChild(tag);
        });
        
        messageDiv.appendChild(sourcesDiv);
    }

    chatHistory.appendChild(messageDiv);
    
    // Hacer auto-scroll hacia abajo
    chatHistory.scrollTop = chatHistory.scrollHeight;
}
