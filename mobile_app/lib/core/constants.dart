import 'package:flutter/foundation.dart';

class Constants {
  static const String _publicTunnelUrl = 'https://effectiveness-representation-mature-yet.trycloudflare.com/api/v1';
  static const String _localUrl = 'http://127.0.0.1:8000/api/v1';

  // Automatically connects to local backend when tested on Web/Desktop, and public tunnel on phone!
  static String get apiBaseUrl => kIsWeb ? _localUrl : _publicTunnelUrl;
}
