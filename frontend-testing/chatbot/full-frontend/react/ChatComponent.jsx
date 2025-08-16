import React, { useState } from 'react';
import { sendChatMessage } from './AzureChatService';

const ChatComponent = () => {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setIsLoading(true);
    setError(null);
    
    try {
      // Tambahkan pesan pengguna ke percakapan
      const userMessage = { role: 'user', content: message };
      const updatedConversation = [...conversation, userMessage];
      setConversation(updatedConversation);
      
      // Kirim langsung ke Azure OpenAI
      const response = await sendChatMessage(message, updatedConversation);

      // Tambahkan balasan bot ke percakapan
      const botMessage = { role: 'assistant', content: response.reply };
      setConversation(prev => [...prev, botMessage]);
      
      setMessage('');
    } catch (err) {
      setError(err.message || 'Terjadi kesalahan saat memproses permintaan');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h1>Azure OpenAI Chatbot (Direct)</h1>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="chat-messages">
        {conversation.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'Anda' : 'Bot'}:</strong> {msg.content}
          </div>
        ))}
        {isLoading && <div className="message loading">Bot sedang mengetik...</div>}
      </div>
      
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ketik pesan Anda..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !message.trim()}>
          {isLoading ? 'Mengirim...' : 'Kirim'}
        </button>
      </form>
    </div>
  );
};

export default ChatComponent;