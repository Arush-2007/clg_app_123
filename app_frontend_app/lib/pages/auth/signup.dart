import 'package:college_app/pages/auth/login_post_email.dart';
import 'package:college_app/pages/auth/login.dart';
import 'package:college_app/services/auth_methods.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
//TODO: Refine UI and add more animations
class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  late final TextEditingController emailController;
  late final TextEditingController passwordController;
  late final TextEditingController confirmPasswordController;
  bool _obscurePassword = true;
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    emailController = TextEditingController();
    passwordController = TextEditingController();
    confirmPasswordController = TextEditingController();
  }

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> onSignUpWithEmail() async {
    setState(() => isLoading = true);

    final email = emailController.text.trim();
    final password = passwordController.text.trim();
    final confirmPassword = confirmPasswordController.text.trim();

    if (email.isEmpty || password.isEmpty || confirmPassword.isEmpty) {
      showSnackBar('All fields must be filled');
    } else if (password != confirmPassword) {
      showSnackBar('Passwords don\'t match');
    } else {
      try {
        final result = await AuthMethods().signUpUserWithEmail(
          email: email,
          password: password,
        );

        if (result.isAccountCreated) {
          showSnackBar('Account created! Please verify your email.');
          Future.delayed(const Duration(seconds: 2), () {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => const LoginPostScreen()),
            );
          });
        } else {
          showSnackBar(result.message);
        }
      } catch (e) {
        showSnackBar('Network error: $e');
      }
    }

    setState(() => isLoading = false);
  }

  Future<void> onSignUpWithGoogle() async {
    setState(() => isLoading = true);
    try {
      final result = await AuthMethods().signUpUserWithGoogle();
      showSnackBar(result.message);
    } catch (e) {
      showSnackBar('Google sign-in failed: $e');
    }
    setState(() => isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: colors.surface,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              SizedBox(
                height: 250,
                child: Lottie.asset("assets/lottie/welcome.json", fit: BoxFit.contain),
              ),
              const SizedBox(height: 10),
              Text('Create Your Account',
                  style: GoogleFonts.poppins(
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    color: colors.onSurface,
                  )),
              const SizedBox(height: 6),
              Text('Sign up to get started!',
                  style: GoogleFonts.poppins(
                    fontSize: 16,
                    color: colors.onSurface.withOpacity(0.7),
                  )),
              const SizedBox(height: 24),
              Material(
                color: colors.surfaceContainerHighest,
                elevation: 10,
                borderRadius: BorderRadius.circular(16),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
                  child: Column(
                    children: [
                      buildTextField(emailController, 'Email', Icons.email, colors),
                      const SizedBox(height: 12),
                      buildPasswordField(passwordController, 'Password', colors),
                      const SizedBox(height: 12),
                      buildPasswordField(confirmPasswordController, 'Confirm Password', colors),
                      const SizedBox(height: 24),
                      ElevatedButton(
                        onPressed: onSignUpWithEmail,
                        style: ElevatedButton.styleFrom(
                          minimumSize: const Size.fromHeight(50),
                          backgroundColor: colors.primary,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12)),
                        ),
                        child: Text("Create Account",
                            style: GoogleFonts.poppins(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: colors.onPrimary)),
                      ),
                      const SizedBox(height: 20),
                      Row(
                        children: [
                          Expanded(child: Divider(color: colors.primary)),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 12.0),
                            child: Text("or sign up with",
                                style: GoogleFonts.poppins(
                                    color: colors.onSurface.withOpacity(0.7))),
                          ),
                          Expanded(child: Divider(color: colors.primary)),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          GestureDetector(
                              onTap: onSignUpWithGoogle,
                              child: socialIcon("assets/icons/google.png", colors))
                        ],
                      )
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("Already have an account? ",
                      style: GoogleFonts.poppins(color: colors.onSurface)),
                  GestureDetector(
                    onTap: () {
                      Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(builder: (_) => const LoginScreen()),
                      );
                    },
                    child: Text("Login",
                        style: GoogleFonts.poppins(
                            color: colors.primary, fontWeight: FontWeight.w600)),
                  )
                ],
              )
            ],
          ),
        ),
      ),
    );
  }

  Widget buildTextField(TextEditingController controller, String label, IconData icon,
      ColorScheme colors) {
    return TextField(
      controller: controller,
      maxLength: 30,
      decoration: InputDecoration(
        prefixIcon: Icon(icon, color: colors.primary),
        labelText: label,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        counterText: "",
        focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: colors.primary, width: 2)),
        enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: colors.primary, width: 2)),
      ),
      style: GoogleFonts.poppins(fontSize: 16, color: colors.onSurface),
    );
  }

  Widget buildPasswordField(TextEditingController controller, String label,
      ColorScheme colors) {
    return TextField(
      controller: controller,
      obscureText: _obscurePassword,
      maxLength: 30,
      decoration: InputDecoration(
        prefixIcon: Icon(Icons.lock, color: colors.primary),
        suffixIcon: IconButton(
            icon: Icon(
                _obscurePassword ? Icons.visibility_off : Icons.visibility),
            onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
            color: colors.primary),
        labelText: label,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        counterText: "",
        focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: colors.primary, width: 2)),
        enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: colors.primary, width: 2)),
      ),
      style: GoogleFonts.poppins(fontSize: 16, color: colors.onSurface),
    );
  }

  Widget socialIcon(String path, ColorScheme colors) {
    return Container(
      width: 60,
      height: 60,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: colors.primary, width: 2),
        borderRadius: BorderRadius.circular(50),
      ),
      child: Image.asset(path),
    );
  }

  void showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), duration: const Duration(seconds: 2)),
    );
  }
}