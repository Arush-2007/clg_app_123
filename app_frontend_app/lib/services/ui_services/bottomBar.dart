import 'package:college_app/pages/auth/auth_gate.dart';
import 'package:college_app/pages/auth/chat.dart';
import 'package:college_app/pages/auth/home.dart';
import 'package:college_app/pages/clubs/club_registration_screen.dart';
import 'package:college_app/services/auth_methods.dart';
import 'package:curved_navigation_bar/curved_navigation_bar.dart';
import 'package:flutter/material.dart';

//TODO :add function -  Await for user data to be fetched before showing the home screen
class Bottombar extends StatefulWidget {
  final int initialIndex;

  const Bottombar({super.key, this.initialIndex = 0});

  @override
  State<Bottombar> createState() => _BottombarState();
}

class _BottombarState extends State<Bottombar> {
  late int currentIndex;
  late final List<Widget> pages;

  @override
  void initState() {
    super.initState();
    currentIndex = widget.initialIndex;
    pages = const [
      HomeScreen(),
      ConversationsScreen(),
      _ClubsPlaceholderScreen(),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      extendBody: false,
      body: IndexedStack(
        index: currentIndex,
        children: pages,
      ),
      bottomNavigationBar: CurvedNavigationBar(
        backgroundColor: Colors.transparent,
        color: colorScheme.primary,
        buttonBackgroundColor: colorScheme.secondary,
        animationCurve: Curves.easeInOut,
        animationDuration: const Duration(milliseconds: 300),
        height: 65,
        index: currentIndex,
        onTap: (index) {
          setState(() {
            currentIndex = index;
          });
        },
        items: [
          Icon(
            currentIndex == 0 ? Icons.home : Icons.home_outlined,
            color: currentIndex == 0
                ? colorScheme.onSecondary
                : Colors.white,
            size: 28,
          ),
          Icon(
            currentIndex == 1 ? Icons.chat_bubble : Icons.chat_bubble_outline,
            color: currentIndex == 1
                ? colorScheme.onSecondary
                : Colors.white,
            size: 28,
          ),
          Icon(
            Icons.groups,
            color: currentIndex == 2
                ? colorScheme.onSecondary
                : Colors.white,
            size: 28,
          ),
        ],
      ),
    );
  }
}

class _ClubsPlaceholderScreen extends StatelessWidget {
  const _ClubsPlaceholderScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Clubs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () async {
              await AuthMethods().signOut();
              if (!context.mounted) return;
              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const AuthGate()),
                (route) => false,
              );
            },
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              'Club Registration',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const ClubRegistrationScreen(),
                ),
              ),
              child: const Text('Register a Club'),
            ),
          ],
        ),
      ),
    );
  }
}
