import 'package:flutter/material.dart';

class WellnessCheckInScreen extends StatefulWidget {
  const WellnessCheckInScreen({super.key});

  @override
  State<WellnessCheckInScreen> createState() => _WellnessCheckInScreenState();
}

class _WellnessCheckInScreenState extends State<WellnessCheckInScreen> {
  int _currentStep = 0;
  
  // Mock form state (values 1 to 5)
  double _sleepScore = 3;
  double _moodScore = 3;
  double _energyScore = 3;
  double _workloadScore = 3;
  double _stressScore = 3;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Wellness Check-in'),
      ),
      body: Stepper(
        type: StepperType.vertical,
        currentStep: _currentStep,
        onStepContinue: () {
          if (_currentStep < 4) {
            setState(() { _currentStep += 1; });
          } else {
            // Reached the end
            _submitForm();
          }
        },
        onStepCancel: () {
          if (_currentStep > 0) {
            setState(() { _currentStep -= 1; });
          } else {
            Navigator.of(context).pop();
          }
        },
        controlsBuilder: (context, details) {
          final isLastStep = _currentStep == 4;
          return Padding(
            padding: const EdgeInsets.only(top: 24.0),
            child: Row(
              children: [
                ElevatedButton(
                  onPressed: details.onStepContinue,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0D47A1),
                    foregroundColor: Colors.white,
                  ),
                  child: Text(isLastStep ? 'Submit Check-in' : 'Next'),
                ),
                const SizedBox(width: 16),
                if (_currentStep > 0)
                  TextButton(
                    onPressed: details.onStepCancel,
                    child: const Text('Back'),
                  ),
              ],
            ),
          );
        },
        steps: [
          _buildSliderStep(
            title: 'Sleep',
            subtitle: 'Rate your sleep quality and duration',
            value: _sleepScore,
            onChanged: (val) => setState(() => _sleepScore = val),
            isActive: _currentStep >= 0,
          ),
          _buildSliderStep(
            title: 'Mood',
            subtitle: 'How is your mood today?',
            value: _moodScore,
            onChanged: (val) => setState(() => _moodScore = val),
            isActive: _currentStep >= 1,
          ),
          _buildSliderStep(
            title: 'Energy',
            subtitle: 'How energetic do you feel?',
            value: _energyScore,
            onChanged: (val) => setState(() => _energyScore = val),
            isActive: _currentStep >= 2,
          ),
          _buildSliderStep(
            title: 'Workload',
            subtitle: 'How manageable is your current workload?',
            value: _workloadScore,
            onChanged: (val) => setState(() => _workloadScore = val),
            isActive: _currentStep >= 3,
          ),
          _buildSliderStep(
            title: 'Stress',
            subtitle: 'Rate your current stress level',
            value: _stressScore,
            onChanged: (val) => setState(() => _stressScore = val),
            isActive: _currentStep >= 4,
          ),
        ],
      ),
    );
  }

  Step _buildSliderStep({
    required String title,
    required String subtitle,
    required double value,
    required ValueChanged<double> onChanged,
    required bool isActive,
  }) {
    return Step(
      title: Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      subtitle: Text(subtitle),
      isActive: isActive,
      content: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16.0),
        child: Column(
          children: [
            Text(
              '${value.toInt()} / 5',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF0D47A1)),
            ),
            const SizedBox(height: 8),
            Slider(
              value: value,
              min: 1,
              max: 5,
              divisions: 4,
              activeColor: const Color(0xFF00897B),
              label: value.toInt().toString(),
              onChanged: onChanged,
            ),
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Low/Poor', style: TextStyle(color: Colors.grey)),
                Text('High/Good', style: TextStyle(color: Colors.grey)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _submitForm() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Wellness check-in recorded.'),
        backgroundColor: Color(0xFF00897B),
        behavior: SnackBarBehavior.floating,
      ),
    );
    // Add a slight delay before popping to show the snackbar
    Future.delayed(const Duration(seconds: 1), () {
      Navigator.of(context).pop();
    });
  }
}
