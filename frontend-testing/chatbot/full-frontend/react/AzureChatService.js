const { REACT_APP_AZURE_OPENAI_KEY, REACT_APP_AZURE_API_VERSION, 
        REACT_APP_AZURE_OPENAI_ENDPOINT, REACT_APP_DEPLOYMENT_NAME } = process.env;

export const sendChatMessage = async (message, conversationHistory = []) => {
  try {
    const response = await fetch(`${REACT_APP_AZURE_OPENAI_ENDPOINT}/openai/deployments/${REACT_APP_DEPLOYMENT_NAME}/chat/completions?api-version=${REACT_APP_AZURE_API_VERSION}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api-key': REACT_APP_AZURE_OPENAI_KEY
      },
      body: JSON.stringify({
        messages: [
          {
            role: 'system',
            content: 'Anda adalah asisten yang membantu.'
          },
          ...conversationHistory,
          {
            role: 'user',
            content: message
          }
        ]
      })
    });

    if (!response.ok) {
      throw new Error(`Azure OpenAI error: ${response.status}`);
    }

    const data = await response.json();
    return {
      reply: data.choices[0].message.content,
      tokens: data.usage.total_tokens
    };
  } catch (error) {
    console.error('Error calling Azure OpenAI:', error);
    throw error;
  }
};