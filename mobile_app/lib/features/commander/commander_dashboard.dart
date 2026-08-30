import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../main.dart'; // For AuthProvider
import '../auth/login_screen.dart';

class CommanderDashboard extends StatelessWidget {
  const CommanderDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Commander Overview'),
        backgroundColor: const Color(0xFF0D47A1),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              context.read<AuthProvider>().logout();
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Unit Wellness Trends',
              style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF0D47A1)),
            ),
            const SizedBox(height: 16),
            _buildTrendCard('Stress Trend', '↑ 14%', Colors.red),
            const SizedBox(height: 12),
            _buildTrendCard('Fatigue Trend', '↑ 8%', Colors.orange),
            const SizedBox(height: 12),
            _buildTrendCard('Workload Trend', '↑ 11%', Colors.orange),
            const SizedBox(height: 32),
            const Text(
              'Organizational Recommendations',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
              child: const Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    ListTile(
                      leading: Icon(Icons.assignment, color: Color(0xFF0D47A1)),
                      title: Text('Review duty distribution'),
                    ),
                    Divider(),
                    ListTile(
                      leading:
                          Icon(Icons.trending_up, color: Color(0xFF0D47A1)),
                      title: Text('Review workload trends'),
                    ),
                    Divider(),
                    ListTile(
                      leading: Icon(Icons.health_and_safety,
                          color: Color(0xFF0D47A1)),
                      title: Text('Strengthen welfare availability'),
                    ),
                  ],
                ),
              ),
            )
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        selectedItemColor: const Color(0xFF0D47A1),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
              icon: Icon(Icons.pie_chart), label: 'Overview'),
          BottomNavigationBarItem(
              icon: Icon(Icons.show_chart), label: 'Trends'),
          BottomNavigationBarItem(
              icon: Icon(Icons.library_books), label: 'Resources'),
        ],
      ),
    );
  }

  Widget _buildTrendCard(String title, String trend, Color trendColor) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(title,
                style:
                    const TextStyle(fontSize: 18, fontWeight: FontWeight.w500)),
            Text(trend,
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: trendColor)),
          ],
        ),
      ),
    );
  }
}
