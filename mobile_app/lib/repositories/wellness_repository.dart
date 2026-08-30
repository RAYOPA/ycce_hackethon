import '../models/wellness_checkin.dart';

class WellnessHistoryRepository {
  // Mock data representing a 7-day wellness history
  List<WellnessCheckIn> getMockHistory() {
    final now = DateTime.now();
    return [
      // Monday to Sunday as requested
      WellnessCheckIn(
          personnelId: 'P001',
          date: now.subtract(const Duration(days: 6)),
          sleepQuality: 6,
          moodScore: 3,
          energyScore: 3,
          workloadScore: 2,
          stressScore: 2), // Monday
      WellnessCheckIn(
          personnelId: 'P001',
          date: now.subtract(const Duration(days: 5)),
          sleepQuality: 7,
          moodScore: 4,
          energyScore: 4,
          workloadScore: 3,
          stressScore: 3), // Tuesday
      WellnessCheckIn(
          personnelId: 'P001',
          date: now.subtract(const Duration(days: 4)),
          sleepQuality: 8,
          moodScore: 5,
          energyScore: 4,
          workloadScore: 3,
          stressScore: 3), // Wednesday
      WellnessCheckIn(
          personnelId: 'P001',
          date: now.subtract(const Duration(days: 3)),
          sleepQuality: 5,
          moodScore: 2,
          energyScore: 2,
          workloadScore: 5,
          stressScore: 4), // Thursday
      WellnessCheckIn(
          personnelId: 'P001',
          date: now.subtract(const Duration(days: 2)),
          sleepQuality: 7,
          moodScore: 4,
          energyScore: 4,
          workloadScore: 4,
          stressScore: 3), // Friday
      WellnessCheckIn(
          personnelId: 'P001',
          date: now.subtract(const Duration(days: 1)),
          sleepQuality: 8,
          moodScore: 5,
          energyScore: 5,
          workloadScore: 2,
          stressScore: 2), // Saturday
      WellnessCheckIn(
          personnelId: 'P001',
          date: now,
          sleepQuality: 7,
          moodScore: 4,
          energyScore: 4,
          workloadScore: 2,
          stressScore: 3), // Sunday
    ];
  }

  WellnessCheckIn? getLastCheckIn() {
    final history = getMockHistory();
    if (history.isNotEmpty) {
      return history.last;
    }
    return null;
  }
}
