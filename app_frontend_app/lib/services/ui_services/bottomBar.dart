import 'package:college_app/pages/auth/chat.dart';
import 'package:college_app/pages/auth/home.dart';
import 'package:flutter/material.dart';
import 'package:curved_navigation_bar/curved_navigation_bar.dart';
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
      ChatScreen(),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    

    // now the bottom navigation bar will retain the state of the current page
    // and the selected page will be highlighted with the appropriate colors
    return Scaffold(
      extendBody: false,
      body: IndexedStack(
        index: currentIndex,
        children: pages,
      ),
      bottomNavigationBar: CurvedNavigationBar(
        backgroundColor: Colors.transparent,
        color: colorScheme.primary, // Fire color (#FF5722)
        buttonBackgroundColor: colorScheme.secondary, // Fire accent (#FFD54F)
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
                ? colorScheme.onSecondary // Black on amber for active
                : Colors.white, // White on fire red for inactive
            size: 28,
          ),
          Icon(
            currentIndex == 1 ? Icons.chat_bubble : Icons.chat_bubble_outline,
            color: currentIndex == 1 
                ? colorScheme.onSecondary // Black on amber for active
                : Colors.white, // White on fire red for inactive
            size: 28,
          ),
        ],
      ),
    );
  }
}