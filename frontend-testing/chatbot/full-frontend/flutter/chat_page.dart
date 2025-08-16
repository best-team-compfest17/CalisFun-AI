import 'package:flutter/material.dart';
import 'azure_openai_service.dart';

class ChatPage extends StatefulWidget {
  @override
  _ChatPageState createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  final AzureOpenAIService _openAIService = AzureOpenAIService();
  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(role: 'user', content: message));
      _isLoading = true;
      _errorMessage = '';
      _messageController.clear();
    });

    try {

      // Kirim langsung ke Azure OpenAI (ini tempat untuk testing kirim message ke chatbotnya dan nerima response balik)

      final conversationHistory = _messages
          .map((msg) => {'role': msg.role, 'content': msg.content})
          .toList();
      
      final response = await _openAIService.sendMessage(message, conversationHistory);

      setState(() {
        _messages.add(ChatMessage(role: 'assistant', content: response['reply']));
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Azure OpenAI Chat (Direct)'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.all(8.0),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index < _messages.length) {
                  final message = _messages[index];
                  return ChatBubble(
                    text: message.content,
                    isUser: message.role == 'user',
                  );
                } else {
                  return Padding(
                    padding: EdgeInsets.all(8.0),
                    child: Text(
                      'Bot sedang mengetik...',
                      style: TextStyle(
                        fontStyle: FontStyle.italic,
                        color: Colors.grey,
                      ),
                    ),
                  );
                }
              },
            ),
          ),
          if (_errorMessage.isNotEmpty)
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 8.0),
              child: Text(
                _errorMessage,
                style: TextStyle(color: Colors.red),
              ),
            ),
          Padding(
            padding: EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: 'Ketik pesan Anda...',
                      border: OutlineInputBorder(),
                    ),
                    enabled: !_isLoading,
                  ),
                ),
                SizedBox(width: 8.0),
                IconButton(
                  icon: Icon(Icons.send),
                  onPressed: _isLoading ? null : _sendMessage,
                  color: Colors.blue,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ChatMessage {
  final String role;
  final String content;

  ChatMessage({required this.role, required this.content});
}

class ChatBubble extends StatelessWidget {
  final String text;
  final bool isUser;

  const ChatBubble({required this.text, required this.isUser});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 4.0),
        padding: EdgeInsets.all(12.0),
        decoration: BoxDecoration(
          color: isUser ? Colors.blue[100] : Colors.grey[200],
          borderRadius: BorderRadius.circular(12.0),
        ),
        child: Text(text),
      ),
    );
  }
}