import 'package:flutter/material.dart';
import '../../models/consent_settings.dart';

// Brand Colors
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color mutedGreen = Color(0xFF8BBB92);
const Color backgroundLight = Color(0xFFF1F3E0);

class ManageConsentScreen extends StatefulWidget {
  final ConsentSettings initialSettings;
  final ValueChanged<ConsentSettings> onSaved;

  const ManageConsentScreen({
    super.key,
    required this.initialSettings,
    required this.onSaved,
  });

  @override
  State<ManageConsentScreen> createState() => _ManageConsentScreenState();
}

class _ManageConsentScreenState extends State<ManageConsentScreen> {
  late ConsentSettings _settings;

  @override
  void initState() {
    super.initState();
    // Copy the initial settings
    _settings = ConsentSettings(
      wellnessCheckIn: widget.initialSettings.wellnessCheckIn,
      selfAssessment: widget.initialSettings.selfAssessment,
      optionalSensors: widget.initialSettings.optionalSensors,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        title:
            const Text('Manage Consent', style: TextStyle(color: primaryNavy)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: primaryNavy),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            // Save on back
            widget.onSaved(_settings);
            Navigator.of(context).pop();
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
                'You control what information you choose to share.',
                style: TextStyle(
                  color: primaryNavy,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 32),
              Container(
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
                  children: [
                    _buildSwitchTile(
                      title: 'Wellness Check-ins',
                      value: _settings.wellnessCheckIn,
                      onChanged: (val) {
                        setState(() {
                          _settings.wellnessCheckIn = val;
                        });
                      },
                    ),
                    const Divider(height: 1, color: Colors.black12),
                    _buildSwitchTile(
                      title: 'Self-assessment',
                      value: _settings.selfAssessment,
                      onChanged: (val) {
                        setState(() {
                          _settings.selfAssessment = val;
                        });
                      },
                    ),
                    const Divider(height: 1, color: Colors.black12),
                    _buildSwitchTile(
                      title: 'Optional Sensors',
                      value: _settings.optionalSensors,
                      onChanged: (val) {
                        setState(() {
                          _settings.optionalSensors = val;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              color: Colors.black87,
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: Colors.white,
            activeTrackColor: mutedGreen,
            inactiveThumbColor: Colors.white,
            inactiveTrackColor: Colors.grey.shade300,
          ),
        ],
      ),
    );
  }
}
