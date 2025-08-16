import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ChatPage extends StatefulWidget {
  @override
  _ChatPageState createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
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
      // Ganti URL dengan endpoint API Anda
      final url = Uri.parse('http://localhost:5000/chat');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'message': message}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _messages.add(ChatMessage(role: 'bot', content: data['reply']));
        });
      } else {
        throw Exception('Failed to get response from chatbot');
      }
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
        title: Text('Azure OpenAI Chatbot'),
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