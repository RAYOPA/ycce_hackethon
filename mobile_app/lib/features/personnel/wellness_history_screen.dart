import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../repositories/wellness_repository.dart';
import 'wellness_checkin_screen.dart';
import 'home_screen.dart';

// Brand Colors
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color mutedGreen = Color(0xFF8BBB92);
const Color backgroundLight = Color(0xFFF1F3E0);

class WellnessHistoryScreen extends StatefulWidget {
  const WellnessHistoryScreen({super.key});

  @override
  State<WellnessHistoryScreen> createState() => _WellnessHistoryScreenState();
}

class _WellnessHistoryScreenState extends State<WellnessHistoryScreen> {
  final _repository = WellnessHistoryRepository();

  @override
  Widget build(BuildContext context) {
    final history = _repository.getMockHistory();
    final lastCheckIn = _repository.getLastCheckIn();

    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        title: const Text('Wellness History',
            style: TextStyle(color: primaryNavy)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: primaryNavy),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            // Check if we are inside the bottom nav bar (PersonnelHome)
            final state = context.findAncestorStateOfType<PersonnelHomeState>();
            if (state != null) {
              state.setIndex(0); // Go back to Home tab
            } else {
              Navigator.of(context).pop();
            }
          },
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Your wellbeing',
                style: TextStyle(
                  color: primaryNavy,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Track your patterns over time.',
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 32),

              // SECTION 1: STRESS TREND
              _buildChartCard(
                title: 'Stress Trend',
                data: history.map((e) => e.stressScore.toDouble()).toList(),
                lineColor: primaryNavy, // Using navy instead of red
                minY: 0,
                maxY: 5,
              ),
              const SizedBox(height: 24),

              // SECTION 2: SUMMARY CARDS
              Row(
                children: [
                  Expanded(
                    child: _buildSummaryCard(
                      icon: Icons.bedtime_outlined,
                      iconColor: mutedGreen,
                      title: 'Sleep',
                      value: '6.8 h',
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildSummaryCard(
                      icon: Icons.mood,
                      iconColor: secondaryTeal,
                      title: 'Mood',
                      value: '3.8 / 5',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // SECTION 3: MOOD TREND
              _buildChartCard(
                title: 'Mood Trend',
                data: history.map((e) => e.moodScore.toDouble()).toList(),
                lineColor: secondaryTeal,
                minY: 0,
                maxY: 5,
              ),
              const SizedBox(height: 24),

              // SECTION 4: WORKLOAD TREND
              _buildChartCard(
                title: 'Workload Trend',
                data: history.map((e) => e.workloadScore.toDouble()).toList(),
                lineColor: mutedGreen,
                minY: 0,
                maxY: 5,
              ),
              const SizedBox(height: 24),

              // SECTION 5: LAST CHECK-IN
              _buildLastCheckInCard(lastCheckIn?.date),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSummaryCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
  }) {
    return Container(
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: iconColor, size: 20),
              const SizedBox(width: 8),
              Text(title, style: const TextStyle(color: Colors.black54)),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(
              color: primaryNavy,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChartCard({
    required String title,
    required List<double> data,
    required Color lineColor,
    required double minY,
    required double maxY,
  }) {
    return Container(
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
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
                minY: minY,
                maxY: maxY,
                lineBarsData: [
                  LineChartBarData(
                    spots: data
                        .asMap()
                        .entries
                        .map((e) => FlSpot(e.key.toDouble(), e.value))
                        .toList(),
                    isCurved: true,
                    color: lineColor,
                    barWidth: 3,
                    isStrokeCapRound: true,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: lineColor.withOpacity(0.1),
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
              Text('Mon',
                  style: TextStyle(color: Colors.black38, fontSize: 12)),
              Text('Sun',
                  style: TextStyle(color: Colors.black38, fontSize: 12)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLastCheckInCard(DateTime? lastDate) {
    final dateStr = lastDate != null
        ? 'Today • ${DateFormat('h:mm a').format(lastDate)}'
        : 'No recent check-ins';

    return Container(
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Last Check-in',
            style: TextStyle(
              color: primaryNavy,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            dateStr,
            style: const TextStyle(color: Colors.black87),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {
                // Navigate to Wellness Check-in tab
                final state =
                    context.findAncestorStateOfType<PersonnelHomeState>();
                if (state != null) {
                  state.setIndex(1); // Index of Check-in
                } else {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                        builder: (_) => const WellnessCheckInScreen()),
                  );
                }
              },
              style: OutlinedButton.styleFrom(
                foregroundColor: secondaryTeal,
                side: const BorderSide(color: secondaryTeal),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.add, size: 20),
                  SizedBox(width: 8),
                  Text('+ New Check-in',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
