import 'package:flutter/material.dart';
import '../../repositories/wellness_repository.dart';
import 'wellness_checkin_success_screen.dart';

// Brand Colors
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color mutedGreen = Color(0xFF8BBB92);
const Color backgroundLight = Color(0xFFF1F3E0);

class WellnessCheckInScreen extends StatefulWidget {
  const WellnessCheckInScreen({super.key});

  @override
  State<WellnessCheckInScreen> createState() => _WellnessCheckInScreenState();
}

class _WellnessCheckInScreenState extends State<WellnessCheckInScreen> {
  int? _sleepScore;
  int? _moodScore;
  int? _energyScore;
  int? _workloadScore;
  int? _stressScore;

  bool _showError = false;

  bool _isSubmitting = false;

  Future<void> _submit() async {
    if (_sleepScore == null ||
        _moodScore == null ||
        _energyScore == null ||
        _workloadScore == null ||
        _stressScore == null) {
      setState(() {
        _showError = true;
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final repo = WellnessRepository();
      // stressScore mapped loosely, or we send it as string based on business rules
      // For backend: stress_level enum is usually LOW, MODERATE, HIGH
      String stressLevel = 'LOW';
      if (_stressScore! >= 4) stressLevel = 'HIGH';
      else if (_stressScore! == 3) stressLevel = 'MODERATE';

      await repo.submitCheckin(
        physicalScore: _energyScore!,
        mentalScore: _moodScore!,
        sleepHours: _sleepScore!.toDouble() * 2, // approximation
        stressLevel: stressLevel,
      );

      if (!mounted) return;
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const WellnessCheckInSuccessScreen()),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceAll('Exception: ', '')),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        title: const Text('Wellness Check-in',
            style: TextStyle(color: primaryNavy)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: primaryNavy),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'How are you feeling today?',
                style: TextStyle(
                  color: primaryNavy,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Take a moment for yourself.',
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 32),
              if (_showError)
                Container(
                  margin: const EdgeInsets.only(bottom: 24),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.shade200),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.red, size: 20),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Please complete all questions to proceed.',
                          style: TextStyle(color: Colors.red),
                        ),
                      ),
                    ],
                  ),
                ),
              _buildQuestionSection(
                title: 'How well did you sleep?',
                selectedValue: _sleepScore,
                onSelected: (val) => setState(() {
                  _sleepScore = val;
                  _showError = false;
                }),
              ),
              _buildQuestionSection(
                title: 'How is your mood?',
                selectedValue: _moodScore,
                onSelected: (val) => setState(() {
                  _moodScore = val;
                  _showError = false;
                }),
              ),
              _buildQuestionSection(
                title: 'How is your energy?',
                selectedValue: _energyScore,
                onSelected: (val) => setState(() {
                  _energyScore = val;
                  _showError = false;
                }),
              ),
              _buildQuestionSection(
                title: 'How heavy is your workload?',
                selectedValue: _workloadScore,
                onSelected: (val) => setState(() {
                  _workloadScore = val;
                  _showError = false;
                }),
              ),
              _buildQuestionSection(
                title: 'How stressed do you feel?',
                selectedValue: _stressScore,
                onSelected: (val) => setState(() {
                  _stressScore = val;
                  _showError = false;
                }),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: secondaryTeal,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 0,
                  ),
                  child: _isSubmitting
                      ? const SizedBox(
                          height: 24,
                          width: 24,
                          child: CircularProgressIndicator(color: Colors.white),
                        )
                      : const Text('Submit Check-in',
                          style: TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 16)),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuestionSection({
    required String title,
    required int? selectedValue,
    required Function(int) onSelected,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 24),
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
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: List.generate(5, (index) {
              final val = index + 1;
              final isSelected = selectedValue == val;
              return GestureDetector(
                onTap: () => onSelected(val),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: isSelected ? mutedGreen : Colors.grey.shade100,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: isSelected ? mutedGreen : Colors.grey.shade300,
                      width: 2,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      val.toString(),
                      style: TextStyle(
                        color: isSelected ? Colors.white : Colors.black54,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                ),
              );
            }),
          ),
          const SizedBox(height: 12),
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('1 = Low',
                  style: TextStyle(color: Colors.black45, fontSize: 12)),
              Text('5 = High',
                  style: TextStyle(color: Colors.black45, fontSize: 12)),
            ],
          ),
        ],
      ),
    );
  }
}
