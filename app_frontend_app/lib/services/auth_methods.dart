import 'dart:convert';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;


/// A class to handle user token and sign-up results
class SignUpResult {
  final String message;
  final String? token;

  SignUpResult({required this.message, this.token});
}

/// A class to handle user token and sign-in results
class SignInResult {
  final String message;
  final String? token;

  SignInResult({required this.message, this.token});
}


/// A class to handle authentication methods including sign-up, sign-in, and sign-out
class AuthMethods {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  //TODO: attach end point here
  final String backendUrl = 'https://yourapi.com/users/';

  // Sign up with Email and Password
  Future<SignUpResult> signUpUserWithEmail({
  required String email,
  required String password,
}) async {
  String res = "Some error occurred";
  String? token;

  try {
    if (email.isNotEmpty && password.isNotEmpty) {
      UserCredential cred = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      await cred.user?.sendEmailVerification();
      token = await cred.user?.getIdToken();

      if (token != null) {
        final response = await http.post(
          Uri.parse(backendUrl),
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'email': email,
            'source': 'email-password',
          }),
        );

        if (response.statusCode == 200) {
          res = "User created, verification email sent, and user synced with backend.";
        } else {
          res = "User created & email sent, but backend rejected token.";
        }
      } else {
        res = "User created but failed to fetch token.";
      }
    } else {
      res = "Please fill in all the fields.";
    }
  } on FirebaseAuthException catch (err) {
    switch (err.code) {
      case 'weak-password':
        res = "The password provided is too weak.";
        break;
      case 'email-already-in-use':
        res = "An account with this email already exists.";
        break;
      case 'invalid-email':
        res = "The email address is invalid.";
        break;
      default:
        res = err.message ?? "An unexpected authentication error occurred.";
    }
  } catch (e) {
    res = "Something went wrong. Please try again.";
  }

  return SignUpResult(message: res, token: token);
}


  // Sign in with Email and Password
  Future<SignInResult> signInUserWithEmail({
  required String email,
  required String password,
}) async {
  String res = "Some error occurred";
  String? token;

  try {
    UserCredential userCred = await _auth.signInWithEmailAndPassword(
      email: email,
      password: password,
    );

    if (userCred.user != null && userCred.user!.emailVerified) {
      token = await userCred.user!.getIdToken();

      // 🔁 Push token to backend
      final response = await http.post(
        Uri.parse(backendUrl),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': email,
          'source': 'email-password',
        }),
      );

      if (response.statusCode == 200) {
        res = "Login successful and token synced with backend.";
      } else {
        res = "Login successful but backend rejected the token.";
      }
    } else {
      res = "Please verify your email before logging in.";
    }
  } on FirebaseAuthException catch (err) {
    res = err.message ?? "Firebase auth error";
  } catch (e) {
    res = "Login failed. Try again.";
  }

  return SignInResult(message: res, token: token);
}



  // Sign in or sign up with Google
  Future<SignUpResult> signUpUserWithGoogle() async {
  String res = "Some error occurred";
  String? token;

  try {
    final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
    if (googleUser == null) {
      return SignUpResult(message: "Google Sign-In was cancelled.", token: null);
    }

    final GoogleSignInAuthentication googleAuth = await googleUser.authentication;

    final AuthCredential credential = GoogleAuthProvider.credential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );

    UserCredential userCredential = await _auth.signInWithCredential(credential);
    token = await userCredential.user?.getIdToken();

    if (token != null) {
      final response = await http.post(
        Uri.parse(backendUrl),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': userCredential.user?.email ?? '',
          'source': 'google-signin',
        }),
      );

      if (response.statusCode == 200) {
        res = "Google sign-in success and user synced with backend.";
      } else {
        res = "Google sign-in success, but backend rejected the token.";
      }
    } else {
      res = "User signed in but failed to retrieve token.";
    }
  } catch (e) {
    res = "Google Sign-In failed: ${e.toString()}";
  }

  return SignUpResult(message: res, token: token);
}



///sign out metod
  Future<void> signOut() async {
  await _googleSignIn.signOut();
  await _auth.signOut();
}

//resend verification email method
Future<String> resendVerificationEmail() async {
  try {
    final user = _auth.currentUser;

    if (user == null) {
      return "No user is signed in.";
    }

    if (user.emailVerified) {
      return "Your email is already verified.";
    }

    await user.sendEmailVerification();
    return "Verification email sent again.";
  } catch (e) {
    return "Failed to resend verification email.";
  }
}

}
