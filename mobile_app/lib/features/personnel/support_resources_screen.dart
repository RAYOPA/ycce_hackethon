import 'package:flutter/material.dart';

// Brand Colors
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color backgroundLight = Color(0xFFF1F3E0);

class SupportResourcesScreen extends StatelessWidget {
  const SupportResourcesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        title: const Text('Support Resources',
            style: TextStyle(color: primaryNavy)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: primaryNavy),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24.0),
          children: [
            _buildResourceCard(
              icon: Icons.self_improvement,
              title: 'Wellbeing guidance',
              description:
                  'Tips and strategies for managing stress and maintaining mental clarity.',
            ),
            const SizedBox(height: 16),
            _buildResourceCard(
              icon: Icons.bedtime,
              title: 'Rest and recovery resources',
              description:
                  'Best practices for optimizing sleep and physical recovery.',
            ),
            const SizedBox(height: 16),
            _buildResourceCard(
              icon: Icons.psychology,
              title: 'Counselling information',
              description:
                  'How to access professional, confidential counselling services.',
            ),
            const SizedBox(height: 16),
            _buildResourceCard(
              icon: Icons.local_hospital,
              title: 'Emergency support information',
              description:
                  'Immediate contacts for urgent crisis support and medical assistance.',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResourceCard({
    required IconData icon,
    required String title,
    required String description,
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
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: secondaryTeal.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: secondaryTeal, size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
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
                const SizedBox(height: 8),
                Text(
                  description,
                  style: const TextStyle(color: Colors.black87),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
