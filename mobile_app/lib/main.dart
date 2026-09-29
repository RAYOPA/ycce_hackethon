import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import 'core/theme/app_theme.dart';
import 'core/constants.dart';
import 'core/network/api_client.dart';
import 'features/auth/login_screen.dart';

// Entry Point
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Constants.loadCustomBaseUrl();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: const ManRakshakApp(),
    ),
  );
}

// Main App Widget
class ManRakshakApp extends StatelessWidget {
  const ManRakshakApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ManRakshak',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system, // Uses system setting for light/dark
      home: const LoginScreen(),
    );
  }
}

// Auth Provider connected to Backend
class AuthProvider extends ChangeNotifier {
  String? _currentUserRole;
  String? get currentUserRole => _currentUserRole;
  String? _token;
  String? get token => _token;

  Future<void> login(String email, String password) async {
    final response = await ApiClient.post(
      '/auth/login',
      body: {
        'email': email,
        'password': password,
      },
      includeAuth: false,
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _token = data['access_token'];
      final refreshToken = data['refresh_token'];
      
      await ApiClient.saveTokens(_token!, refreshToken);

      // Fetch user profile immediately
      final meResponse = await ApiClient.get('/auth/me');
      if (meResponse.statusCode == 200) {
        final meData = jsonDecode(meResponse.body);
        final role = meData['role'] as String;
        if (role == 'COMMANDER') {
          _currentUserRole = 'Commander';
        } else if (role == 'WELFARE_OFFICER' || role == 'WELFARE') {
          _currentUserRole = 'Welfare';
        } else {
          _currentUserRole = 'Personnel';
        }
        notifyListeners();
      } else {
        await ApiClient.clearTokens();
        throw Exception('Failed to load profile (${meResponse.statusCode})');
      }
    } else {
      String message = 'Failed to login (${response.statusCode})';
      try {
        final error = jsonDecode(response.body);
        if (error is Map && error.containsKey('detail')) {
          message = error['detail'].toString();
        }
      } catch (_) {}
      throw Exception(message);
    }
  }

  Future<void> register({
    required String name,
    required String email,
    required String password,
    String? userCode,
    String? role,
    String? mobileNumber,
  }) async {
    String apiRole = 'PERSONNEL';
    if (role == 'Commander') {
      apiRole = 'COMMANDER';
    } else if (role == 'Welfare Officer' || role == 'Welfare') {
      apiRole = 'WELFARE_OFFICER';
    }

    final response = await ApiClient.post(
      '/auth/register',
      body: {
        'name': name.trim(),
        'email': email.trim().toLowerCase(),
        'password': password,
        'user_code': (userCode != null && userCode.trim().isNotEmpty) ? userCode.trim() : null,
        'role': apiRole,
        'mobile_number': (mobileNumber != null && mobileNumber.trim().isNotEmpty) ? mobileNumber.trim() : null,
      },
      includeAuth: false,
    );

    if (response.statusCode == 201 || response.statusCode == 200) {
      return;
    } else {
      String message = 'Failed to register (${response.statusCode})';
      try {
        final error = jsonDecode(response.body);
        if (error is Map && error.containsKey('detail')) {
          message = error['detail'].toString();
        }
      } catch (_) {}
      throw Exception(message);
    }
  }

  Future<void> logout() async {
    try {
      await ApiClient.post('/auth/logout');
    } catch (_) {} // Ignore network errors on logout
    await ApiClient.clearTokens();
    _currentUserRole = null;
    _token = null;
    notifyListeners();
  }
}

// End of main.dart
