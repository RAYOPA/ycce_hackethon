import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'features/personnel/home_screen.dart';
import 'features/welfare/welfare_dashboard.dart';
import 'features/commander/commander_dashboard.dart';

// Entry Point
void main() {
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
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0D47A1), // Navy Blue primary
          secondary: const Color(0xFF00897B), // Teal secondary
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const SplashScreen(),
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

// Splash Screen
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 2), () {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const LoginScreen()),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.shield, size: 80, color: Color(0xFF0D47A1)),
            SizedBox(height: 16),
            Text(
              'ManRakshak',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Color(0xFF0D47A1),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Login Screen
class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final idController = TextEditingController();
    final pwdController = TextEditingController();

    return Scaffold(
      appBar: AppBar(title: const Text('Login')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: idController,
              decoration: const InputDecoration(
                labelText: 'Personnel ID',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: pwdController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Password',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                context.read<AuthProvider>().login(idController.text, pwdController.text);
                
                final role = context.read<AuthProvider>().currentUserRole;
                Widget target;
                if (role == 'Welfare') {
                  target = const WelfareDashboard();
                } else if (role == 'Commander') {
                  target = const CommanderDashboard();
                } else {
                  target = const PersonnelHome();
                }

                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (context) => target),
                );
              },
              child: const Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}

// End of main.dart
