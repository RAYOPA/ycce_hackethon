import '../models/support_request.dart';
import 'package:flutter/foundation.dart';

class SupportRepository {
  final List<SupportRequest> _mockRequests = [];

  Future<void> submitRequest(SupportRequest request) async {
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));
    _mockRequests.add(request);
    debugPrint('Saved support request: ${request.toJson()}');
  }

  List<SupportRequest> getMyRequests(String personnelId) {
    return _mockRequests
        .where((req) => req.personnelId == personnelId)
        .toList();
  }
}
