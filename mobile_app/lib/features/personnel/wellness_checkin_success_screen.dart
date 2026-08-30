import 'package:flutter/material.dart';

// Brand Colors
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color mutedGreen = Color(0xFF8BBB92);
const Color backgroundLight = Color(0xFFF1F3E0);

class WellnessCheckInSuccessScreen extends StatelessWidget {
  const WellnessCheckInSuccessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(24),
                decoration: const BoxDecoration(
                  color: mutedGreen,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.check, size: 64, color: Colors.white),
              ),
              const SizedBox(height: 32),
              const Text(
                'Check-in recorded',
                style: TextStyle(
                  color: primaryNavy,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              const Text(
                'Thank you for taking a moment for your wellbeing.',
                style: TextStyle(color: Colors.black87, fontSize: 16),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    // Navigate back to Home
                    Navigator.of(context).pop(); // Pops success screen
                    Navigator.of(context)
                        .pop(); // Pops checkin form to go back to Home
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
                  child: const Text('Back to Home',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
