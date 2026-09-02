import 'dart:convert';
import '../core/network/api_client.dart';
import '../models/notification_model.dart';

class NotificationRepository {
  Future<List<NotificationItem>> getNotifications({int page = 1, int pageSize = 50}) async {
    final response = await ApiClient.get('/notifications?page=$page&page_size=$pageSize');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final items = data['items'] as List;
      return items.map((i) => NotificationItem.fromJson(i)).toList();
    } else {
      throw Exception('Failed to load notifications');
    }
  }

  Future<int> getUnreadCount() async {
    final response = await ApiClient.get('/notifications/unread-count');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['count'] ?? 0;
    }
    return 0;
  }

  Future<void> markAsRead(String id) async {
    final response = await ApiClient.put('/notifications/$id/read');
    if (response.statusCode != 200) {
      throw Exception('Failed to mark notification as read');
    }
  }
  
  Future<void> markAllAsRead() async {
    final response = await ApiClient.put('/notifications/read-all');
    if (response.statusCode != 200) {
      throw Exception('Failed to mark all notifications as read');
    }
  }
}
