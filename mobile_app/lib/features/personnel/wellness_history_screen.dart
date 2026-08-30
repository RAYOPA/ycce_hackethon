import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class WellnessHistoryScreen extends StatelessWidget {
  const WellnessHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Wellness History'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Your Trends',
              style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF0D47A1)),
            ),
            const SizedBox(height: 24),
            _buildChartCard('Stress Trend', const Color(0xFFD32F2F),
                [3.0, 3.2, 4.0, 3.8, 3.5, 3.1, 2.9]),
            const SizedBox(height: 24),
            _buildChartCard('Sleep Trend (Hours)', const Color(0xFF1976D2),
                [6.5, 7.0, 5.5, 6.0, 7.5, 8.0, 7.2]),
            const SizedBox(height: 24),
            _buildChartCard('Mood Trend', const Color(0xFF00897B),
                [4.0, 4.2, 3.5, 3.0, 4.5, 4.8, 4.5]),
          ],
        ),
      ),
    );
  }

  Widget _buildChartCard(
      String title, Color lineColor, List<double> dataPoints) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style:
                    const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData:
                      const FlGridData(show: true, drawVerticalLine: false),
                  titlesData: FlTitlesData(
                    show: true,
                    topTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 22,
                        getTitlesWidget: (value, meta) {
                          const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
                          if (value.toInt() >= 0 &&
                              value.toInt() < days.length) {
                            return Text(days[value.toInt()],
                                style: const TextStyle(fontSize: 12));
                          }
                          return const Text('');
                        },
                      ),
                    ),
                  ),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: dataPoints
                          .asMap()
                          .entries
                          .map((e) => FlSpot(e.key.toDouble(), e.value))
                          .toList(),
                      isCurved: true,
                      color: lineColor,
                      barWidth: 4,
                      isStrokeCapRound: true,
                      dotData: const FlDotData(show: true),
                      belowBarData: BarAreaData(
                        show: true,
                        color: lineColor.withValues(alpha: 0.1),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
