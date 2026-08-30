import 'package:flutter/material.dart';
import 'support_request_form_screen.dart';
import 'support_resources_screen.dart';
import 'home_screen.dart';

// Brand Colors
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color mutedGreen = Color(0xFF8BBB92);
const Color backgroundLight = Color(0xFFF1F3E0);

class SupportScreen extends StatelessWidget {
  const SupportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        title:
            const Text('Welfare Support', style: TextStyle(color: primaryNavy)),
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
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "You're not alone.",
                style: TextStyle(
                  color: primaryNavy,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                "Support is available when you need it.",
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 32),

              // CARD 1: Request Support
              _buildSupportCard(
                icon: Icons.chat_bubble_outline,
                title: 'Request Support',
                description: 'Connect with a welfare officer for assistance.',
                buttonText: 'Request Support',
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                        builder: (_) => const SupportRequestFormScreen()),
                  );
                },
                isPrimary: true,
              ),
              const SizedBox(height: 16),

              // CARD 2: Contact Welfare
              _buildSupportCard(
                icon: Icons.phone_outlined,
                title: 'Contact Welfare',
                description: 'Get in touch with your authorized support team.',
                buttonText: 'Contact',
                onPressed: () {
                  _showContactDialog(context);
                },
                isPrimary: false,
              ),
              const SizedBox(height: 16),

              // CARD 3: Support Resources
              _buildSupportCard(
                icon: Icons.library_books_outlined,
                title: 'Support Resources',
                description: 'Explore available wellbeing resources.',
                buttonText: 'View Resources',
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                        builder: (_) => const SupportResourcesScreen()),
                  );
                },
                isPrimary: false,
              ),
              const SizedBox(height: 48),

              // PRIVACY NOTICE
              Center(
                child: Column(
                  children: [
                    const Icon(Icons.lock_outline,
                        color: Colors.black38, size: 24),
                    const SizedBox(height: 8),
                    const Text(
                      'Your request is handled confidentially.',
                      style: TextStyle(color: Colors.black45, fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Sharing information is voluntary.',
                      style: TextStyle(
                          color: Colors.black45.withOpacity(0.5), fontSize: 12),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSupportCard({
    required IconData icon,
    required String title,
    required String description,
    required String buttonText,
    required VoidCallback onPressed,
    required bool isPrimary,
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
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: isPrimary
                      ? secondaryTeal.withOpacity(0.1)
                      : Colors.grey.shade100,
                  shape: BoxShape.circle,
                ),
                child: Icon(icon,
                    color: isPrimary ? secondaryTeal : primaryNavy, size: 24),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    color: primaryNavy,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            description,
            style: const TextStyle(color: Colors.black87),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: isPrimary
                ? ElevatedButton(
                    onPressed: onPressed,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: secondaryTeal,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 0,
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(buttonText,
                            style: const TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 16)),
                        const SizedBox(width: 8),
                        const Icon(Icons.arrow_forward, size: 18),
                      ],
                    ),
                  )
                : OutlinedButton(
                    onPressed: onPressed,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: primaryNavy,
                      side: const BorderSide(color: Colors.black12),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(buttonText,
                            style: const TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 16)),
                        const SizedBox(width: 8),
                        const Icon(Icons.arrow_forward, size: 18),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  void _showContactDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title:
            const Text('Contact Welfare', style: TextStyle(color: primaryNavy)),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Welfare Officer: Sarah Jenkins',
                style: TextStyle(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Phone: 555-0199'),
            SizedBox(height: 8),
            Text('Email: welfare@manrakshak.mock'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
