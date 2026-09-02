import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants.dart';

class ApiClient {
  static const _storage = FlutterSecureStorage();
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  static Future<String?> getAccessToken() async {
    return await _storage.read(key: _accessTokenKey);
  }

  static Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _storage.write(key: _accessTokenKey, value: accessToken);
    await _storage.write(key: _refreshTokenKey, value: refreshToken);
  }

  static Future<void> clearTokens() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }

  static Future<Map<String, String>> _getHeaders({bool includeAuth = true, String? customContentType}) async {
    final headers = <String, String>{
      'Content-Type': customContentType ?? 'application/json',
      'Accept': 'application/json',
    };

    if (includeAuth) {
      final token = await getAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  static Future<http.Response> get(String endpoint, {bool includeAuth = true}) async {
    return _request('GET', endpoint, includeAuth: includeAuth);
  }

  static Future<http.Response> post(String endpoint, {dynamic body, bool includeAuth = true, String? customContentType}) async {
    return _request('POST', endpoint, body: body, includeAuth: includeAuth, customContentType: customContentType);
  }

  static Future<http.Response> put(String endpoint, {dynamic body, bool includeAuth = true}) async {
    return _request('PUT', endpoint, body: body, includeAuth: includeAuth);
  }

  static Future<http.Response> patch(String endpoint, {dynamic body, bool includeAuth = true}) async {
    return _request('PATCH', endpoint, body: body, includeAuth: includeAuth);
  }

  static Future<http.Response> delete(String endpoint, {bool includeAuth = true}) async {
    return _request('DELETE', endpoint, includeAuth: includeAuth);
  }

  static Future<http.Response> _request(
    String method,
    String endpoint, {
    dynamic body,
    bool includeAuth = true,
    bool isRetry = false,
    String? customContentType,
  }) async {
    final url = Uri.parse('${Constants.apiBaseUrl}$endpoint');
    var headers = await _getHeaders(includeAuth: includeAuth, customContentType: customContentType);

    http.Response response;
    final timeout = const Duration(seconds: 15);

    try {
      if (method == 'GET') {
        response = await http.get(url, headers: headers).timeout(timeout);
      } else if (method == 'POST') {
        final requestBody = customContentType == 'application/x-www-form-urlencoded' ? body : (body != null ? jsonEncode(body) : null);
        response = await http.post(url, headers: headers, body: requestBody).timeout(timeout);
      } else if (method == 'PUT') {
        response = await http.put(url, headers: headers, body: body != null ? jsonEncode(body) : null).timeout(timeout);
      } else if (method == 'PATCH') {
        response = await http.patch(url, headers: headers, body: body != null ? jsonEncode(body) : null).timeout(timeout);
      } else if (method == 'DELETE') {
        response = await http.delete(url, headers: headers).timeout(timeout);
      } else {
        throw Exception('Unsupported HTTP method');
      }

      // Handle 401 Unauthorized -> Refresh Token
      if (response.statusCode == 401 && includeAuth && !isRetry) {
        final success = await _refreshToken();
        if (success) {
          return _request(method, endpoint, body: body, includeAuth: includeAuth, isRetry: true, customContentType: customContentType);
        } else {
          await clearTokens();
          // Returning 401 for upstream to handle logout
          return response; 
        }
      }

      return response;
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<bool> _refreshToken() async {
    final refreshToken = await _storage.read(key: _refreshTokenKey);
    if (refreshToken == null) return false;

    final url = Uri.parse('${Constants.apiBaseUrl}/auth/refresh');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh_token': refreshToken}),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final newAccessToken = data['access_token'];
        await _storage.write(key: _accessTokenKey, value: newAccessToken);
        // Backend doesn't issue a new refresh token on refresh right now
        return true;
      }
    } catch (_) {}

    return false;
  }
}
