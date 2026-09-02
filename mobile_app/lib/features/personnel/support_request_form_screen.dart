import 'package:flutter/material.dart';
import '../../models/support_request.dart';
import '../../repositories/support_repository.dart';

// Brand Colors
const Color primaryNavy = Color(0xFF092328);
const Color secondaryTeal = Color(0xFF12544F);
const Color mutedGreen = Color(0xFF8BBB92);
const Color backgroundLight = Color(0xFFF1F3E0);

class SupportRequestFormScreen extends StatefulWidget {
  const SupportRequestFormScreen({super.key});

  @override
  State<SupportRequestFormScreen> createState() =>
      _SupportRequestFormScreenState();
}

class _SupportRequestFormScreenState extends State<SupportRequestFormScreen> {
  final _repository = SupportRepository();
  final _messageController = TextEditingController();
  String? _selectedOption;

  final List<String> _options = [
    'General wellbeing',
    'Workload concerns',
    'Fatigue / rest',
    'Personal support',
    'Prefer to discuss privately',
  ];

  bool _isSubmitting = false;

  Future<void> _submit() async {
    if (_selectedOption == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select how we can support you.')),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      // Map option to category (backend enum usually expects uppercase without spaces, we will send mapped or original)
      String category = 'GENERAL_WELLBEING';
      if (_selectedOption!.contains('Workload')) category = 'WORKLOAD';
      else if (_selectedOption!.contains('Fatigue')) category = 'FATIGUE';
      else if (_selectedOption!.contains('Personal')) category = 'PERSONAL_SUPPORT';
      else if (_selectedOption!.contains('private')) category = 'PRIVATE_DISCUSSION';

      await _repository.submitRequest(
        category: category,
        priority: 'STANDARD',
        message: _messageController.text.trim(),
      );

      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
        _showConfirmationDialog();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: Colors.red),
        );
      }
    }
  }

  void _showConfirmationDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.check_circle, color: mutedGreen),
            SizedBox(width: 8),
            Text('Request Submitted'),
          ],
        ),
        content: const Text(
          'Support request submitted.\n\nAn authorized welfare officer can follow up with you.',
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop(); // Close dialog
              Navigator.of(context).pop(); // Go back to Support Screen
            },
            child: const Text('Back to Support',
                style: TextStyle(
                    color: secondaryTeal, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        title:
            const Text('Request Support', style: TextStyle(color: primaryNavy)),
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
                'How can we support you?',
                style: TextStyle(
                  color: primaryNavy,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),
              ..._options.map((option) => Padding(
                    padding: const EdgeInsets.only(bottom: 12.0),
                    child: InkWell(
                      onTap: () {
                        setState(() {
                          _selectedOption = option;
                        });
                      },
                      borderRadius: BorderRadius.circular(12),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: _selectedOption == option
                                ? secondaryTeal
                                : Colors.grey.shade300,
                            width: 2,
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              _selectedOption == option
                                  ? Icons.radio_button_checked
                                  : Icons.radio_button_off,
                              color: _selectedOption == option
                                  ? secondaryTeal
                                  : Colors.grey.shade400,
                            ),
                            const SizedBox(width: 12),
                            Text(
                              option,
                              style: TextStyle(
                                fontSize: 16,
                                color: _selectedOption == option
                                    ? primaryNavy
                                    : Colors.black87,
                                fontWeight: _selectedOption == option
                                    ? FontWeight.w600
                                    : FontWeight.normal,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  )),
              const SizedBox(height: 24),
              const Text(
                'Optional message',
                style: TextStyle(
                  color: primaryNavy,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _messageController,
                maxLines: 4,
                decoration: InputDecoration(
                  hintText: 'Add a note (optional)',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: Colors.grey.shade300),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: Colors.grey.shade300),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide:
                        const BorderSide(color: secondaryTeal, width: 2),
                  ),
                ),
              ),
              const SizedBox(height: 48),
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
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2),
                        )
                      : const Text('Submit Request',
                          style: TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 16)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
