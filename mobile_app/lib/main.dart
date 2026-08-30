import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
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

// Mock Auth Provider
class AuthProvider extends ChangeNotifier {
  String? _currentUserRole;
  String? get currentUserRole => _currentUserRole;

  void login(String id, String password) {
    if (id.startsWith('P')) {
      _currentUserRole = 'Personnel';
    } else if (id.startsWith('W')) {
      _currentUserRole = 'Welfare';
    } else if (id.startsWith('C')) {
      _currentUserRole = 'Commander';
    } else {
      _currentUserRole = 'Personnel'; // Default fallback
    }
    notifyListeners();
  }

  void logout() {
    _currentUserRole = null;
    notifyListeners();
  }
}

// End of main.dart
