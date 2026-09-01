import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'core/theme/app_theme.dart';
import 'core/constants.dart';
import 'features/auth/login_screen.dart';

// Entry Point
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // TODO: Add firebase_options.dart and use DefaultFirebaseOptions.currentPlatform
  // await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

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
    final url = Uri.parse('${Constants.apiBaseUrl}/auth/login');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _token = data['access_token'];
      
      final role = data['user']['role'] as String;
      // Map backend roles to frontend expected roles
      if (role == 'COMMANDER') {
        _currentUserRole = 'Commander';
      } else if (role == 'WELFARE_OFFICER' || role == 'WELFARE') {
        _currentUserRole = 'Welfare';
      } else {
        _currentUserRole = 'Personnel';
      }
      notifyListeners();
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
    final url = Uri.parse('${Constants.apiBaseUrl}/auth/register');
    
    // Map frontend role string to backend enum
    String backendRole = 'PERSONNEL';
    if (role == 'Commander') {
      backendRole = 'COMMANDER';
    } else if (role == 'Welfare Officer' || role == 'Welfare') {
      backendRole = 'WELFARE_OFFICER';
    }

    final payload = {
      'name': name.trim(),
      'email': email.trim().toLowerCase(),
      'password': password,
      'user_code': (userCode != null && userCode.trim().isNotEmpty) ? userCode.trim() : null,
      'role': backendRole,
      'mobile_number': (mobileNumber != null && mobileNumber.trim().isNotEmpty) ? mobileNumber.trim() : null,
    };

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );

    if (response.statusCode == 201 || response.statusCode == 200) {
      return;
    } else {
      String message = 'Registration failed (${response.statusCode})';
      try {
        final error = jsonDecode(response.body);
        if (error is Map && error.containsKey('detail')) {
          message = error['detail'].toString();
        }
      } catch (_) {}
      throw Exception(message);
    }
  }

  void logout() {
    _currentUserRole = null;
    _token = null;
    notifyListeners();
  }
}

// End of main.dart
