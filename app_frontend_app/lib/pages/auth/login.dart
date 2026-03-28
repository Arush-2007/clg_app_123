import 'package:college_app/pages/auth/auth_gate.dart';
import 'package:college_app/pages/auth/signup.dart';
import 'package:college_app/services/auth_methods.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
//TODO: Refine UI and add more animations
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  late TextEditingController emailController;
  late TextEditingController passwordController;
  bool _obscurePassword = true;

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
                height: 320,
                child: Lottie.asset(
                  "assets/lottie/login.json",
                  fit: BoxFit.contain,
                ),
              ),
              Text(
                'Welcome Back!',
                style: GoogleFonts.poppins(
                  fontSize: 30,
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onSurface,
                ),
              ),
              SizedBox(height: 20),

              // Form Card
              Material(
                shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(16),
    side: BorderSide(color: colorScheme.primary, width: 1),
  ),
                elevation: 10,
                color: colorScheme.surfaceContainerHighest,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
                  child: Column(
                    children: [
                      // Email
                      TextField(
                        controller: emailController,
                        keyboardType: TextInputType.emailAddress,
                        maxLength: 30,
                        decoration: InputDecoration(
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: colorScheme.primary, width: 2),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: colorScheme.primary, width: 2),
                          ),
                          hintText: 'Enter your Email',
                          labelText: 'Email',
                          prefixIcon: Icon(Icons.email, color: colorScheme.primary),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          counterText: "",
                        ),
                        style: GoogleFonts.poppins(fontSize: 16, color: colorScheme.onSurface),
                      ),

                      SizedBox(height: 12),

                      // Password
                      TextField(
                        controller: passwordController,
                        keyboardType: TextInputType.visiblePassword,
                        obscureText: _obscurePassword,
                        maxLength: 30,
                        decoration: InputDecoration(
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: colorScheme.primary, width: 2),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: colorScheme.primary, width: 2),
                          ),
                          hintText: 'Enter your Password',
                          labelText: 'Password',
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
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          counterText: "",
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
                                    style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
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
                                        keyboardType: TextInputType.emailAddress,
                                        decoration: InputDecoration(
                                          hintText: 'Email address',
                                          border: OutlineInputBorder(
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  actions: [
                                    TextButton(
                                      onPressed: () => Navigator.pop(context),
                                      child: Text('Cancel', style: GoogleFonts.poppins()),
                                    ),
                                    ElevatedButton(
                                      onPressed: () async {
                                        final navigator = Navigator.of(context);
                                        final messenger = ScaffoldMessenger.of(context);
                                        final result = await AuthMethods().sendPasswordResetEmail(
                                          email: emailController.text,
                                        );
                                        navigator.pop();
                                        messenger.showSnackBar(
                                          SnackBar(content: Text(result)),
                                        );
                                      },
                                      child: Text('Send Reset Link', style: GoogleFonts.poppins()),
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

                      SizedBox(height: 10),

                      // Login Button
                      InkWell(
                        splashColor: colorScheme.primary,
                        onTap: () async {
                          String email = emailController.text.trim();
                          String password = passwordController.text.trim();
                          if (email.isNotEmpty && password.isNotEmpty) {
                            // Call your login method here
                            final signInResult = await AuthMethods().signInUserWithEmail(email: email, password: password);
                            if (signInResult.isBackendSynced) {
                              // ignore: use_build_context_synchronously
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text(signInResult.message)),
                              );
                              Navigator.of(context).pushReplacement(
                                MaterialPageRoute(builder: (_) => const AuthGate()),
                              );
                            } else {
                              // ignore: use_build_context_synchronously
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text("Login failed. Please try again - ${signInResult.message}")),
                              );
                            }
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text("Please fill in all fields.")),
                            );
                          }
                        },
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          width: double.infinity,
                          height: 50,
                          decoration: BoxDecoration(
                            color: colorScheme.primary,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          alignment: Alignment.center,
                          child: Text(
                            "Login",
                            style: GoogleFonts.poppins(
                              fontSize: 18,
                              color: colorScheme.onPrimary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),

                      SizedBox(height: 24),

                      // OR Divider
                      Row(
                        children: [
                          Expanded(child: Divider(color: colorScheme.primary)),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 12.0),
                            child: Text(
                              "or continue with",
                              style: GoogleFonts.poppins(color: theme.textTheme.bodyMedium?.color),
                            ),
                          ),
                          Expanded(child: Divider(color: colorScheme.primary)),
                        ],
                      ),

                      SizedBox(height: 16),

                      // Social Icons
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          Container(
                            width: 60,
                            height: 60,
                            padding: EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              border: Border.all(color: colorScheme.primary, width: 2),
                              borderRadius: BorderRadius.circular(50),
                            ),
                            child: InkWell(
                              borderRadius: BorderRadius.circular(50),
                              onTap: () async {
                                final signInResult = await AuthMethods().signUpUserWithGoogle();
                                if (!mounted) return;
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text(signInResult.message)),
                                );
                                if (signInResult.isBackendSynced) {
                                  Navigator.of(context).pushReplacement(
                                    MaterialPageRoute(builder: (_) => const AuthGate()),
                                  );
                                }
                              },
                              child: Image.asset("assets/icons/google.png"),
                            ),
                          ),
                          //TODO: Add in production stage
                          /*
                          Container(
                            width: 60,
                            height: 60,
                            padding: EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              border: Border.all(color: colorScheme.primary, width: 2),
                              borderRadius: BorderRadius.circular(50),
                            ),
                            child: Image.asset("assets/icons/facebook.png"),
                          ),
                          */
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              SizedBox(height: 16),

              // Sign Up
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "Don't have an account? ",
                    style: GoogleFonts.poppins(color: colorScheme.onSurface),
                  ),
                  GestureDetector(
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => SignUpScreen(),
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
