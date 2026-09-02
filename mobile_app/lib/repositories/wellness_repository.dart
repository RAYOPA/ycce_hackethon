import 'dart:convert';
import '../core/network/api_client.dart';
import '../models/wellness_model.dart';

class WellnessRepository {
  Future<void> submitCheckin({
    required int physicalScore,
    required int mentalScore,
    required double sleepHours,
    required String stressLevel,
    String? notes,
  }) async {
    final payload = {
      'physical_score': physicalScore,
      'mental_score': mentalScore,
      'sleep_hours': sleepHours,
      'stress_level': stressLevel,
      if (notes != null && notes.isNotEmpty) 'notes': notes,
    };
    final response = await ApiClient.post('/wellness/checkins', body: payload);
    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception(_parseError(response.body, 'Failed to submit check-in'));
    }
  }

  Future<List<WellnessCheckin>> getMyHistory({int page = 1, int pageSize = 50}) async {
    final response = await ApiClient.get('/wellness/me?page=$page&page_size=$pageSize');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final items = data['items'] as List;
      return items.map((i) => WellnessCheckin.fromJson(i)).toList();
    } else {
      throw Exception('Failed to load wellness history');
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
