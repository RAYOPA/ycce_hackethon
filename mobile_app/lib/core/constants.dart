import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class Constants {
  static const _storage = FlutterSecureStorage();
  static const _customServerUrlKey = 'custom_server_url';

  static const String defaultLocalIp = '10.235.150.155';
  static const String defaultPort = '8000';
  static const String defaultApiPath = '/api/v1';

  static String? _customServerUrl;

  static Future<void> loadCustomBaseUrl() async {
    try {
      final saved = await _storage.read(key: _customServerUrlKey);
      if (saved != null && saved.trim().isNotEmpty) {
        _customServerUrl = saved.trim();
      }
    } catch (_) {}
  }

  static Future<void> setCustomBaseUrl(String url) async {
    String cleanUrl = url.trim();
    if (cleanUrl.endsWith('/')) {
      cleanUrl = cleanUrl.substring(0, cleanUrl.length - 1);
    }
    if (!cleanUrl.endsWith('/api/v1') && !cleanUrl.contains('/api/')) {
      cleanUrl = '$cleanUrl/api/v1';
    }
    _customServerUrl = cleanUrl;
    await _storage.write(key: _customServerUrlKey, value: cleanUrl);
  }

  static Future<void> resetToDefault() async {
    _customServerUrl = null;
    await _storage.delete(key: _customServerUrlKey);
  }

  static String get defaultBaseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:$defaultPort$defaultApiPath';
    }
    if (defaultTargetPlatform == TargetPlatform.android || defaultTargetPlatform == TargetPlatform.iOS) {
      return 'http://$defaultLocalIp:$defaultPort$defaultApiPath';
    }
    return 'http://127.0.0.1:$defaultPort$defaultApiPath';
  }

  static String get apiBaseUrl {
    if (_customServerUrl != null && _customServerUrl!.isNotEmpty) {
      return _customServerUrl!;
    }
    return defaultBaseUrl;
  }

  static Future<bool> testServerConnection([String? testUrl]) async {
    final baseUrl = testUrl ?? apiBaseUrl;
    final healthUri = Uri.parse('${baseUrl.replaceAll('/api/v1', '')}/health');
    final rootUri = Uri.parse(baseUrl);

    try {
      final res = await http.get(healthUri).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) return true;
    } catch (_) {}

    try {
      final res = await http.get(rootUri).timeout(const Duration(seconds: 4));
      if (res.statusCode < 500) return true;
    } catch (_) {}

    return false;
  }
}

