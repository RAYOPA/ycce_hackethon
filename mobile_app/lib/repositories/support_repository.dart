import 'dart:convert';
import '../core/network/api_client.dart';
import '../models/support_model.dart';

class SupportRepository {
  Future<void> submitRequest({
    required String category,
    required String priority,
    required String message,
  }) async {
    final payload = {
      'category': category,
      'priority': priority,
      'message': message,
    };
    final response = await ApiClient.post('/support', body: payload);
    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception(_parseError(response.body, 'Failed to submit support request'));
    }
  }

  Future<List<SupportRequest>> getMyRequests({int page = 1, int pageSize = 50}) async {
    final response = await ApiClient.get('/support/me?page=$page&page_size=$pageSize');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final items = data['items'] as List;
      return items.map((i) => SupportRequest.fromJson(i)).toList();
    } else {
      throw Exception('Failed to load support requests');
    }
  }

  String _parseError(String body, String defaultMsg) {
    try {
      final data = jsonDecode(body);
      if (data['detail'] != null) return data['detail'].toString();
    } catch (_) {}
    return defaultMsg;
  }
}
