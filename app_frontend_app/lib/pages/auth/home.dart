import 'package:college_app/services/ui_services/list_builder.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:college_app/theme/animated_container.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final List<Map<String, String>> ongoingEvents = [
      {
        'title': 'Event 1',
        'imageURL': 'assets/images/testing/xyz.gif',
      },
      {
        'title': 'Event 2',
        'imageURL': 'assets/images/testing/xyz.gif',
      },
      {
        'title': 'Event 3',
        'imageURL': 'assets/images/testing/xyz.gif',
      },
    ];

    final List<Map<String, String>> upcomingEvents = [];

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(4, 0, 4, 16),
          child: Material(
            elevation: isDarkMode ? 8 : 4,
            shadowColor: colorScheme.primary.withAlpha(51),
            color: colorScheme.surface,
            borderRadius: BorderRadius.circular(28),
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  /// 🔥 Gradient Header
                  Container(
                    margin: const EdgeInsets.all(24),
                    child: AnimatedGradientContainer(
                      builder: (context, alignment1, alignment2) {
                        return Material(
                          elevation: 12,
                          borderRadius: BorderRadius.circular(28),
                          shadowColor: colorScheme.primary.withAlpha(102),
                          child: Container(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                begin: alignment1,
                                end: alignment2,
                                colors: [
                                  colorScheme.primary,
                                  colorScheme.secondary,
                                  colorScheme.primary.withAlpha(230),
                                ],
                                stops: const [0.0, 0.6, 1.0],
                              ),
                              borderRadius: BorderRadius.circular(28),
                              boxShadow: [
                                BoxShadow(
                                  color: colorScheme.primary.withAlpha(128),
                                  blurRadius: 24,
                                  offset: const Offset(0, 12),
                                  spreadRadius: 2,
                                ),
                                BoxShadow(
                                  color: colorScheme.secondary.withAlpha(77),
                                  blurRadius: 16,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            padding: const EdgeInsets.all(28),
                            child: Row(
                              children: [
                                /// Greeting Text
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          Text(
                                            'Hey, User!',
                                            style: GoogleFonts.poppins(
                                              fontSize: 20,
                                              fontWeight: FontWeight.w700,
                                              height: 1.2,
                                              color: Colors.white,
                                            ),
                                          ),

                                        ],
                                      ),
                                      const SizedBox(height: 8),
                                      Text(
                                        'Ready to ignite your day?',
                                        style: GoogleFonts.poppins(
                                          fontSize: 16,
                                          fontWeight: FontWeight.w500,
                                          color: Colors.white.withAlpha(242),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),

                                /// Fire Icon Badge
                                Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: Colors.white.withAlpha(38),
                                    border: Border.all(
                                      color: Colors.white.withAlpha(102),
                                      width: 2,
                                    ),
                                  ),
                                  child: Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: Colors.white.withAlpha(26),
                                    ),
                                    child: const Icon(
                                      Icons.local_fire_department_rounded,
                                      size: 32,
                                      color: Colors.white,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),

                  /// 💬 Chippo AI Chat Box
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    child: GestureDetector(
                      //TODO: Implement Navigation to Chat AI Screen
                      //onTap: 
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
                        decoration: BoxDecoration(
                          color: isDarkMode
                              ? colorScheme.primary.withAlpha(26)
                              : colorScheme.secondary.withAlpha(26),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: colorScheme.primary.withAlpha(51),
                            width: 1,
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: colorScheme.primary.withAlpha(38),
                                shape: BoxShape.circle,
                              ),
                              child: Icon(
                                Icons.auto_awesome,
                                color: colorScheme.primary,
                                size: 20,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              'Chat with Chippo AI',
                              style: GoogleFonts.poppins(
                                fontSize: 22,
                                fontWeight: FontWeight.w600,
                                color: colorScheme.onSurface,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 36),

                  /// 📌 Ongoing Events
                  _buildEventSection(
                    context,
                    'Ongoing Events',
                    ongoingEvents,
                    Icons.play_circle_fill_rounded,
                    colorScheme,
                    isDarkMode,
                  ),

                  const SizedBox(height: 28),

                  /// 📆 Upcoming Events
                  _buildEventSection(
                    context,
                    'Upcoming Events',
                    upcomingEvents,
                    Icons.schedule,
                    colorScheme,
                    isDarkMode,
                  ),

                  const SizedBox(height: 28),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEventSection(
    BuildContext context,
    String title,
    List<Map<String, String>> events,
    IconData icon,
    ColorScheme colorScheme,
    bool isDarkMode,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          /// Header
          Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  colorScheme.primary.withAlpha(26),
                  colorScheme.secondary.withAlpha(13),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: colorScheme.primary.withAlpha(51),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        colorScheme.primary,
                        colorScheme.secondary,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: colorScheme.primary.withAlpha(77),
                        blurRadius: 8,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Icon(icon, color: Colors.white, size: 24),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Text(
                    title,
                    style: GoogleFonts.poppins(
                      fontSize: 20,
                      fontWeight: FontWeight.w600,
                      color: colorScheme.onSurface,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: colorScheme.primary.withAlpha(26),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${events.length}',
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: colorScheme.primary,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          /// Event Card List
          Container(
            decoration: BoxDecoration(
              color: colorScheme.surface,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                color: colorScheme.primary.withAlpha(26),
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: isDarkMode
                      ? colorScheme.primary.withAlpha(26)
                      : colorScheme.primary.withAlpha(20),
                  blurRadius: 20,
                  offset: const Offset(0, 8),
                  spreadRadius: 1,
                ),
              ],
            ),
            padding: const EdgeInsets.all(20),
            child: ListBuilderWidget(
              items: events,
              type: 'events',
            ),
          ),
        ],
      ),
    );
  }
}
