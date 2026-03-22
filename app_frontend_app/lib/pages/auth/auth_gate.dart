import 'package:college_app/pages/auth/login_post_email.dart';
import 'package:college_app/pages/auth/profile_setup.dart';
import 'package:college_app/pages/auth/login.dart';
import 'package:college_app/services/auth_methods.dart';
import 'package:college_app/services/ui_services/bottomBar.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  Future<Widget> _resolveLoggedInTarget(User user) async {
    final providerIds = user.providerData.map((p) => p.providerId).toSet();
    final usesPassword = providerIds.contains("password");
    if (usesPassword && !user.emailVerified) {
      return const LoginPostScreen();
    }

    final token = await user.getIdToken();
    if (token == null) {
      return const LoginScreen();
    }

    try {
      final hasProfile = await AuthMethods().hasProfile(token: token);
      return hasProfile ? const Bottombar() : const ProfileSetupScreen();
    } catch (_) {
      return const ProfileSetupScreen();
    }
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        final user = snapshot.data;
        if (user == null) {
          return const LoginScreen();
        }

        return FutureBuilder<Widget>(
          future: _resolveLoggedInTarget(user),
          builder: (context, routeSnapshot) {
            if (routeSnapshot.connectionState == ConnectionState.waiting) {
              return const Scaffold(
                body: Center(child: CircularProgressIndicator()),
              );
            }
            return routeSnapshot.data ?? const LoginScreen();
          },
        );
      },
    );
  }
}
