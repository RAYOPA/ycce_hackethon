import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'wellness_checkin_screen.dart';
import 'wellness_history_screen.dart';
import 'support_screen.dart';
import 'profile_screen.dart';
import 'notifications_screen.dart';
import '../../models/user_model.dart';
import '../../repositories/personnel_repository.dart';
import '../../repositories/notification_repository.dart';

// Brand Colors from previous specification
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color mutedGreen = Color(0xFF8BBB92);
const Color backgroundLight = Color(0xFFF1F3E0);

class PersonnelHome extends StatefulWidget {
  const PersonnelHome({super.key});

  @override
  State<PersonnelHome> createState() => PersonnelHomeState();
}

class PersonnelHomeState extends State<PersonnelHome> {
  int _currentIndex = 0;
  UserProfile? _profile;
  bool _isLoadingProfile = true;

  int _unreadNotifCount = 0;
  final _notifRepo = NotificationRepository();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoadingProfile = true);
    await _loadProfile();
    await _refreshUnreadCount();
  }

  Future<void> _refreshUnreadCount() async {
    try {
      final count = await _notifRepo.getUnreadCount();
      if (mounted) setState(() => _unreadNotifCount = count);
    } catch (_) {}
  }

  Future<void> _loadProfile() async {
    try {
      final repo = PersonnelRepository();
      final profile = await repo.getMyProfile();
      if (mounted) {
        setState(() {
          _profile = profile;
          _isLoadingProfile = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingProfile = false;
        });
      }
    }
  }

  void setIndex(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  List<Widget> get _screens => [
    _HomeView(profile: _profile, isLoading: _isLoadingProfile),
    const WellnessCheckInScreen(),
    const WellnessHistoryScreen(),
    const SupportScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      body: _screens[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          selectedItemColor: secondaryTeal,
          unselectedItemColor: Colors.grey.shade400,
          elevation: 0,
          items: const [
            BottomNavigationBarItem(
                icon: Icon(Icons.home_outlined),
                activeIcon: Icon(Icons.home),
                label: 'Home'),
            BottomNavigationBarItem(
                icon: Icon(Icons.favorite_outline),
                activeIcon: Icon(Icons.favorite),
                label: 'Wellness'),
            BottomNavigationBarItem(
                icon: Icon(Icons.history_outlined),
                activeIcon: Icon(Icons.history),
                label: 'History'),
            BottomNavigationBarItem(
                icon: Icon(Icons.support_agent_outlined),
                activeIcon: Icon(Icons.support_agent),
                label: 'Support'),
            BottomNavigationBarItem(
                icon: Icon(Icons.person_outline),
                activeIcon: Icon(Icons.person),
                label: 'Profile'),
          ],
        ),
      ),
    );
  }
}

class _HomeView extends StatelessWidget {
  final UserProfile? profile;
  final bool isLoading;

  const _HomeView({this.profile, this.isLoading = false});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // TOP BAR
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Image.asset(
                      'assets/images/logo.png',
                      height: 32,
                      fit: BoxFit.contain,
                      errorBuilder: (context, error, stackTrace) => const Icon(Icons.shield, color: secondaryTeal, size: 28),
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      'ManRakshak',
                      style: TextStyle(
                        color: primaryNavy,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Row(
                  children: [
                    Stack(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.notifications_none,
                              color: primaryNavy),
                          onPressed: () async {
                            await Navigator.of(context).push(
                              MaterialPageRoute(builder: (_) => const NotificationsScreen()),
                            );
                            _refreshUnreadCount();
                          },
                        ),
                        if (_unreadNotifCount > 0)
                          Positioned(
                            right: 8,
                            top: 8,
                            child: Container(
                              padding: const EdgeInsets.all(4),
                              decoration: const BoxDecoration(
                                color: Colors.redAccent,
                                shape: BoxShape.circle,
                              ),
                              constraints: const BoxConstraints(
                                minWidth: 16,
                                minHeight: 16,
                              ),
                              child: Text(
                                '$_unreadNotifCount',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const CircleAvatar(
                      backgroundColor: secondaryTeal,
                      radius: 16,
                      child: Icon(Icons.person, size: 20, color: Colors.white),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 32),

            // GREETING
            const Text(
              'Good morning,',
              style: TextStyle(
                color: Colors.black54,
                fontSize: 16,
              ),
            ),
            isLoading
                ? const CircularProgressIndicator()
                : Text(
                    profile != null ? '${profile!.name} (${profile!.userCode})' : 'Personnel User',
                    style: const TextStyle(
                      color: primaryNavy,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
            const SizedBox(height: 32),

            // WELLNESS CHECK-IN CARD
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Today's Wellness",
                    style: TextStyle(
                      color: primaryNavy,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    "How are you feeling today?",
                    style: TextStyle(color: Colors.black87),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        // Navigate to Wellness tab
                        final state = context
                            .findAncestorStateOfType<PersonnelHomeState>();
                        state?.setIndex(1); // Index of Wellness CheckIn
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: secondaryTeal,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        elevation: 0,
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text('Start Check-in',
                              style: TextStyle(
                                  fontWeight: FontWeight.bold, fontSize: 16)),
                          SizedBox(width: 8),
                          Icon(Icons.arrow_forward, size: 20),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // WELLNESS SUMMARY
            Row(
              children: [
                Expanded(
                  child: _buildCard(
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.bedtime_outlined,
                                color: mutedGreen, size: 20),
                            SizedBox(width: 8),
                            Text('Sleep',
                                style: TextStyle(color: Colors.black54)),
                          ],
                        ),
                        SizedBox(height: 12),
                        Text(
                          '7.1 h',
                          style: TextStyle(
                            color: primaryNavy,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildCard(
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.mood, color: secondaryTeal, size: 20),
                            SizedBox(width: 8),
                            Text('Mood',
                                style: TextStyle(color: Colors.black54)),
                          ],
                        ),
                        SizedBox(height: 12),
                        Text(
                          '4 / 5',
                          style: TextStyle(
                            color: primaryNavy,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // RECENT WELLNESS TREND (Line Chart)
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Recent Trend",
                    style: TextStyle(
                      color: primaryNavy,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    height: 150,
                    child: LineChart(
                      LineChartData(
                        gridData: const FlGridData(show: false),
                        titlesData: const FlTitlesData(show: false),
                        borderData: FlBorderData(show: false),
                        minX: 0,
                        maxX: 6,
                        minY: 0,
                        maxY: 5,
                        lineBarsData: [
                          LineChartBarData(
                            spots: const [
                              FlSpot(0, 3.5),
                              FlSpot(1, 3.8),
                              FlSpot(2, 4.0),
                              FlSpot(3, 3.2),
                              FlSpot(4, 4.2),
                              FlSpot(5, 4.5),
                              FlSpot(6, 4.0),
                            ],
                            isCurved: true,
                            color: mutedGreen,
                            barWidth: 3,
                            isStrokeCapRound: true,
                            dotData: const FlDotData(show: false),
                            belowBarData: BarAreaData(
                              show: true,
                              color: mutedGreen.withOpacity(0.1),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('7 days ago',
                          style:
                              TextStyle(color: Colors.black38, fontSize: 12)),
                      Text('Today',
                          style:
                              TextStyle(color: Colors.black38, fontSize: 12)),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // SUPPORT CARD
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.support_agent_outlined, color: secondaryTeal),
                      SizedBox(width: 8),
                      Text(
                        "Need Support?",
                        style: TextStyle(
                          color: primaryNavy,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    "Connect with welfare support when you need it.",
                    style: TextStyle(color: Colors.black87),
                  ),
                  const SizedBox(height: 16),
                  OutlinedButton(
                    onPressed: () {
                      final state =
                          context.findAncestorStateOfType<PersonnelHomeState>();
                      state?.setIndex(3); // Index of Support Screen
                    },
                    style: OutlinedButton.styleFrom(
                      foregroundColor: secondaryTeal,
                      side: const BorderSide(color: secondaryTeal),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.symmetric(
                          vertical: 12, horizontal: 24),
                    ),
                    child: const Text('Get Welfare Support',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildCard({required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: child,
    );
  }
}
