import 'dart:convert';
import '../core/network/api_client.dart';
import '../models/user_model.dart';

class PersonnelRepository {
  Future<UserProfile> getMyProfile() async {
    final response = await ApiClient.get('/personnel/me');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return UserProfile.fromJson(data);
    } else {
      throw Exception('Failed to load profile');
    }
  }
}
