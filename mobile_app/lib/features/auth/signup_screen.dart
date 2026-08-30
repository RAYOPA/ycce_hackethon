import 'package:flutter/material.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _formKey = GlobalKey<FormState>();
  final nameController = TextEditingController();
  final idController = TextEditingController();
  final emailController = TextEditingController();
  final phoneController = TextEditingController();
  final pwdController = TextEditingController();
  final confirmPwdController = TextEditingController();

  String? _selectedRole = 'Personnel';
  bool _agreePrivacy = false;
  bool _obscurePassword = true;
  bool _obscureConfirm = true;

  final List<String> _roles = ['Personnel', 'Welfare Officer', 'Commander'];

  void _handleSignup() {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    if (!_agreePrivacy) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('You must agree to the Privacy Policy')),
      );
      return;
    }
    if (pwdController.text != confirmPwdController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Passwords do not match')),
      );
      return;
    }

    // TODO: Implement actual signup logic via API
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Account Created Successfully')),
    );

    // Go back to login screen
    Navigator.of(context).pop();
  }

  void _showPrivacyPolicy() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Privacy & Consent Policy'),
        content: const SingleChildScrollView(
          child: Text(
            'This is the Privacy and Consent Policy for ManRakshak.\n\n'
            '1. Data Collection: We collect your wellness check-in data, including sleep, mood, and stress levels, '
            'to provide personalized wellness recommendations.\n\n'
            '2. Data Usage: Your data is analyzed securely using our AI engine to identify trends and potential fatigue risks.\n\n'
            '3. Data Sharing: We do not share your individual data with third parties. Anonymized, aggregated data may be '
            'visible to welfare officers or commanders to assess overall unit health without revealing your identity.\n\n'
            '4. Consent: By checking the box, you consent to the collection and use of this data as described above. '
            'You may revoke this consent or request data deletion at any time by contacting support.\n\n'
            'Please read carefully before proceeding.',
          ),
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Create Account'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: theme.textTheme.bodyLarge?.color,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding:
                const EdgeInsets.symmetric(horizontal: 32.0, vertical: 16.0),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 500),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Center(
                      child: Icon(
                        Icons.shield,
                        size: 60,
                        color: theme.primaryColor,
                      ),
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Join ManRakshak',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),

                    // Full Name
                    _buildTextField(
                        'Full Name', Icons.person_outline, nameController),
                    const SizedBox(height: 16),

                    // Personnel ID
                    _buildTextField(
                        'Personnel ID', Icons.badge_outlined, idController),
                    const SizedBox(height: 16),

                    // Email
                    _buildTextField('Email / Official Email',
                        Icons.email_outlined, emailController,
                        keyboardType: TextInputType.emailAddress),
                    const SizedBox(height: 16),

                    // Phone Number
                    _buildTextField(
                        'Phone Number', Icons.phone_outlined, phoneController,
                        keyboardType: TextInputType.phone),
                    const SizedBox(height: 16),

                    // Role Dropdown
                    Text(
                      'Role',
                      style: theme.textTheme.bodyMedium
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<String>(
                      initialValue: _selectedRole,
                      items: _roles.map((role) {
                        return DropdownMenuItem(
                          value: role,
                          child: Text(role),
                        );
                      }).toList(),
                      onChanged: (val) {
                        setState(() {
                          _selectedRole = val;
                        });
                      },
                      decoration: const InputDecoration(
                        prefixIcon: Icon(Icons.work_outline),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Password
                    _buildPasswordField(
                        'Password', pwdController, _obscurePassword, () {
                      setState(() {
                        _obscurePassword = !_obscurePassword;
                      });
                    }),
                    const SizedBox(height: 16),

                    // Confirm Password
                    _buildPasswordField('Confirm Password',
                        confirmPwdController, _obscureConfirm, () {
                      setState(() {
                        _obscureConfirm = !_obscureConfirm;
                      });
                    }),
                    const SizedBox(height: 24),

                    // Agree Checkbox
                    Row(
                      children: [
                        Checkbox(
                          value: _agreePrivacy,
                          onChanged: (val) {
                            setState(() {
                              _agreePrivacy = val ?? false;
                            });
                          },
                        ),
                        Expanded(
                          child: Wrap(
                            crossAxisAlignment: WrapCrossAlignment.center,
                            children: [
                              const Text('I agree to the '),
                              InkWell(
                                onTap: _showPrivacyPolicy,
                                child: Text(
                                  'Privacy & Consent Policy',
                                  style: TextStyle(
                                    color: theme.primaryColor,
                                    fontWeight: FontWeight.bold,
                                    decoration: TextDecoration.underline,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 32),

                    // Signup Button
                    ElevatedButton(
                      onPressed: _handleSignup,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: const Text(
                        'Sign Up',
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(
      String label, IconData icon, TextEditingController controller,
      {TextInputType keyboardType = TextInputType.text}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          decoration: InputDecoration(
            hintText: 'Enter $label',
            prefixIcon: Icon(icon),
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter your $label';
            }
            if (keyboardType == TextInputType.emailAddress &&
                !value.contains('@')) {
              return 'Please enter a valid email';
            }
            if (keyboardType == TextInputType.phone && value.length < 10) {
              return 'Please enter a valid phone number';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildPasswordField(String label, TextEditingController controller,
      bool obscureText, VoidCallback onToggle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          obscureText: obscureText,
          decoration: InputDecoration(
            hintText: 'Enter $label',
            prefixIcon: const Icon(Icons.lock_outline),
            suffixIcon: IconButton(
              icon: Icon(
                obscureText ? Icons.visibility_off : Icons.visibility,
              ),
              onPressed: onToggle,
            ),
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Please enter your $label';
            }
            if (value.length < 6) {
              return 'Password must be at least 6 characters';
            }
            return null;
          },
        ),
      ],
    );
  }
}
