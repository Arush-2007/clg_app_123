import 'package:college_app/pages/auth/auth_gate.dart';
import 'package:college_app/pages/auth/signup.dart';
import 'package:college_app/services/auth_methods.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
//TODO: Refine UI and add more animations
class LoginPostScreen extends StatefulWidget {
  const LoginPostScreen({super.key});

  @override
  State<LoginPostScreen> createState() => _LoginPostScreenState();
}

class _LoginPostScreenState extends State<LoginPostScreen> {
  late TextEditingController emailController;
  late TextEditingController passwordController;
  bool _obscurePassword = true;
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    emailController = TextEditingController();
    passwordController = TextEditingController();
  }

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  void showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  /// Resend verification email - we do not need to ask user to enter email again
  Future<void> resendVerificationEmail() async {
    setState(() => isLoading = true);

    try {
      final message = await AuthMethods().resendVerificationEmail();
      showSnackBar(message);
    } catch (e) {
      showSnackBar("Failed to send email: $e");
    }

    setState(() => isLoading = false);
  }

  Future<void> loginUser() async {
  final email = emailController.text.trim();
  final password = passwordController.text.trim();

  if (email.isEmpty || password.isEmpty) {
    showSnackBar("Please fill in both fields");
    return;
  }

  setState(() => isLoading = true);

  try {
    final result = await AuthMethods().signInUserWithEmail(
      email: email,
      password: password,
    );

    showSnackBar(result.message);

    if (result.isBackendSynced) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const AuthGate()),
      );
    }
  } catch (e) {
    showSnackBar("Login failed: ${e.toString()}");
  }

  setState(() => isLoading = false);
}


  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              SizedBox(
                height: 300,
                child: Lottie.asset("assets/lottie/login.json", fit: BoxFit.contain),
              ),
              Text(
                'Welcome Back!',
                style: GoogleFonts.poppins(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onSurface,
                ),
              ),
              const SizedBox(height: 16),
              Material(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(color: colorScheme.primary),
                ),
                elevation: 10,
                color: colorScheme.surfaceContainerHighest,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
                  child: Column(
                    children: [
                      TextField(
                        controller: emailController,
                        maxLength: 30,
                        keyboardType: TextInputType.emailAddress,
                        decoration: InputDecoration(
                          prefixIcon: Icon(Icons.email, color: colorScheme.primary),
                          labelText: 'Email',
                          hintText: 'Enter your email',
                          counterText: "",
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: colorScheme.primary, width: 2),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: colorScheme.primary, width: 2),
                          ),
                        ),
                        style: GoogleFonts.poppins(fontSize: 16, color: colorScheme.onSurface),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: passwordController,
                        obscureText: _obscurePassword,
                        maxLength: 30,
                        decoration: InputDecoration(
                          prefixIcon: Icon(Icons.lock, color: colorScheme.primary),
                          suffixIcon: IconButton(
                            icon: Icon(
                              _obscurePassword ? Icons.visibility_off : Icons.visibility,
                              color: colorScheme.primary,
                            ),
                            onPressed: () {
                              setState(() {
                                _obscurePassword = !_obscurePassword;
                              });
                            },
                          ),
                          labelText: 'Password',
                          hintText: 'Enter your password',
                          counterText: "",
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: colorScheme.primary, width: 2),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: colorScheme.primary, width: 2),
                          ),
                        ),
                        style: GoogleFonts.poppins(fontSize: 16, color: colorScheme.onSurface),
                      ),
                        Align(
                        alignment: Alignment.centerRight,
                        child: TextButton(
                          onPressed: () {
                            showDialog(
                              context: context,
                              builder: (context) {
                                final emailController = TextEditingController();
                                return AlertDialog(
                                  title: Text(
                                    'Reset Password',
                                    style: GoogleFonts.poppins(
                                        fontWeight: FontWeight.w600),
                                  ),
                                  content: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text(
                                        'Enter your email and we will send you a reset link.',
                                        style: GoogleFonts.poppins(fontSize: 14),
                                      ),
                                      const SizedBox(height: 16),
                                      TextField(
                                        controller: emailController,
                                        keyboardType:
                                            TextInputType.emailAddress,
                                        decoration: InputDecoration(
                                          hintText: 'Email address',
                                          border: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(12),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  actions: [
                                    TextButton(
                                      onPressed: () =>
                                          Navigator.pop(context),
                                      child: Text('Cancel',
                                          style: GoogleFonts.poppins()),
                                    ),
                                    ElevatedButton(
                                      onPressed: () async {
                                        final navigator =
                                            Navigator.of(context);
                                        final messenger =
                                            ScaffoldMessenger.of(context);
                                        final result = await AuthMethods()
                                            .sendPasswordResetEmail(
                                          email: emailController.text,
                                        );
                                        navigator.pop();
                                        messenger.showSnackBar(
                                          SnackBar(content: Text(result)),
                                        );
                                      },
                                      child: Text('Send Reset Link',
                                          style: GoogleFonts.poppins()),
                                    ),
                                  ],
                                );
                              },
                            );
                          },
                          child: Text(
                            "Forgot Password?",
                            style: GoogleFonts.poppins(
                              color: colorScheme.primary,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      InkWell(
                        onTap: loginUser,
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          width: double.infinity,
                          height: 50,
                          decoration: BoxDecoration(
                            color: colorScheme.primary,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          alignment: Alignment.center,
                          child: isLoading
                              ? const CircularProgressIndicator(color: Colors.white)
                              : Text(
                                  "Login",
                                  style: GoogleFonts.poppins(
                                    fontSize: 18,
                                    color: colorScheme.onPrimary,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextButton(
                        onPressed: resendVerificationEmail,
                        child: Text(
                          "Resend Verification Email",
                          style: GoogleFonts.poppins(
                            color: colorScheme.primary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("Need to make new account? ",
                      style: GoogleFonts.poppins(color: colorScheme.onSurface)),
                  GestureDetector(
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => const SignUpScreen(),
                        ),
                      );
                    },
                    child: Text(
                      "Sign Up",
                      style: GoogleFonts.poppins(
                        color: colorScheme.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
