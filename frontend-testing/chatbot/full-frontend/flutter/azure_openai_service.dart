import 'dart:convert';
import 'package:http/http.dart' as http;

class AzureOpenAIService {
  static const String _apiKey = 'your-api-key-here';
  static const String _apiVersion = '2023-05-15';
  static const String _endpoint = 'https://your-resource-name.openai.azure.com';
  static const String _deploymentName = 'gpt-35-turbo';

  Future<Map<String, dynamic>> sendMessage(
      String message, List<Map<String, dynamic>> conversationHistory) async {
    final url = Uri.parse(
        '$_endpoint/openai/deployments/$_deploymentName/chat/completions?api-version=$_apiVersion');

    final messages = [
      {'role': 'system', 'content': 'Anda adalah asisten yang membantu.'},
      ...conversationHistory,
      {'role': 'user', 'content': message}
    ];

    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'api-key': _apiKey,
      },
      body: jsonEncode({
        'messages': messages,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return {
        'reply': data['choices'][0]['message']['content'],
        'tokens': data['usage']['total_tokens'],
      };
    } else {
      throw Exception(
          'Failed to call Azure OpenAI: ${response.statusCode} - ${response.body}');
    }
  }
}