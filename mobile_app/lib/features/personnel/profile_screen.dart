import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/consent_settings.dart';
import '../../models/user_model.dart';
import '../../repositories/personnel_repository.dart';
import '../../main.dart';
import '../auth/login_screen.dart';
import 'home_screen.dart';
import 'manage_consent_screen.dart';
import 'privacy_information_screen.dart';

// Brand Colors
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color mutedGreen = Color(0xFF8BBB92);
const Color backgroundLight = Color(0xFFF1F3E0);

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  ConsentSettings _consentSettings = ConsentSettings();
  UserProfile? _profile;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final repo = PersonnelRepository();
      final profile = await repo.getMyProfile();
      if (mounted) {
        setState(() {
          _profile = profile;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        title: const Text('Profile', style: TextStyle(color: primaryNavy)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: primaryNavy),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            // Check if we are inside the bottom nav bar
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
              // PROFILE HEADER
              if (_isLoading)
                const Center(child: CircularProgressIndicator())
              else if (_profile != null)
                Center(
                  child: Column(
                    children: [
                      Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: secondaryTeal.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.person,
                            color: secondaryTeal, size: 40),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        _profile!.name,
                        style: const TextStyle(
                          color: primaryNavy,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Unit ${_profile!.unitId ?? 'Unknown'}',
                        style: const TextStyle(
                          color: Colors.black54,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 40),

              // PERSONAL INFORMATION CARD
              _buildSectionTitle('Personal Information'),
              const SizedBox(height: 16),
              if (_profile != null)
                Container(
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
                    children: [
                      _buildInfoRow('Personnel ID', _profile!.userCode),
                      const Divider(height: 24, color: Colors.black12),
                      _buildInfoRow('Email', _profile!.email),
                      const Divider(height: 24, color: Colors.black12),
                      _buildInfoRow('Unit', _profile!.unitId ?? 'Unknown'),
                    ],
                  ),
                ),
              const SizedBox(height: 32),

              // PRIVACY & CONSENT CARD
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildSectionTitle('Privacy & Consent'),
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                            builder: (_) => const PrivacyInformationScreen()),
                      );
                    },
                    child: const Text('Privacy Info',
                        style: TextStyle(color: secondaryTeal)),
                  ),
                ],
              ),
              const SizedBox(height: 8),
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
                    _buildConsentRow(
                        'Wellness Check-ins', _consentSettings.wellnessCheckIn),
                    const Divider(height: 1, color: Colors.black12),
                    _buildConsentRow(
                        'Self-assessment', _consentSettings.selfAssessment),
                    const Divider(height: 1, color: Colors.black12),
                    _buildConsentRow(
                        'Optional Sensors', _consentSettings.optionalSensors),
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: SizedBox(
                        width: double.infinity,
                        child: OutlinedButton(
                          onPressed: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => ManageConsentScreen(
                                  initialSettings: _consentSettings,
                                  onSaved: (newSettings) {
                                    setState(() {
                                      _consentSettings = newSettings;
                                    });
                                  },
                                ),
                              ),
                            );
                          },
                          style: OutlinedButton.styleFrom(
                            foregroundColor: primaryNavy,
                            side: const BorderSide(color: Colors.black12),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text('Manage Consent',
                                  style:
                                      TextStyle(fontWeight: FontWeight.bold)),
                              SizedBox(width: 8),
                              Icon(Icons.arrow_forward, size: 16),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 48),

              // LOGOUT BUTTON
              Center(
                child: TextButton.icon(
                  onPressed: () async {
                    // Actual logout logic
                    final auth = context.read<AuthProvider>();
                    await auth.logout();
                    if (!mounted) return;
                    Navigator.of(context).pushAndRemoveUntil(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                      (Route<dynamic> route) => false,
                    );
                  },
                  icon: const Icon(Icons.logout, color: Colors.redAccent),
                  label: const Text('Logout',
                      style: TextStyle(color: Colors.redAccent, fontSize: 16)),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 24, vertical: 12),
                  ),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        color: primaryNavy,
        fontSize: 18,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.black54, fontSize: 16),
        ),
        Text(
          value,
          style: const TextStyle(
              color: primaryNavy, fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _buildConsentRow(String label, bool isEnabled) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.black87, fontSize: 16),
          ),
          Row(
            children: [
              Text(
                isEnabled ? 'ON' : 'OFF',
                style: TextStyle(
                  color: isEnabled ? mutedGreen : Colors.black38,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: isEnabled ? mutedGreen : Colors.grey.shade300,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          )
        ],
      ),
    );
  }
}
