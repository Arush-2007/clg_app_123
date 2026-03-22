import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

class ListBuilderWidget extends StatefulWidget {
  final List<Map<String, String>> items;
  final String type;

  const ListBuilderWidget({
    super.key,
    required this.items,
    required this.type,
  });

  @override
  State<ListBuilderWidget> createState() => _ListBuilderWidgetState();
}

class _ListBuilderWidgetState extends State<ListBuilderWidget> {
  late final PageController _pageController;
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(
      viewportFraction: 0.75,
      initialPage: 0,
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  List<Map<String, String>> _arrangedItems() {
    final items = widget.items;
    if (items.length >= 2) {
      return [...items.reversed];
    } else {
      return [...items];
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final items = _arrangedItems();

    if (items.isEmpty) {
      return Container(
        height: 230,
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Text(
              'No Events Available',
              style: TextStyle(
                color: colorScheme.onSurface.withAlpha(180),
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: Lottie.asset(
                  'assets/lottie/cat.json',
                  fit: BoxFit.contain,
                  width: 180,
                ),
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        SizedBox(
          height: 230,
          child: PageView.builder(
            controller: _pageController,
            itemCount: items.length,
            onPageChanged: (index) {
              setState(() => _currentIndex = index);
            },
            itemBuilder: (context, index) {
              final imageURL = items[index]['imageURL']!;
              final title = items[index]['title'] ?? 'Untitled';

              return AnimatedBuilder(
                animation: _pageController,
                builder: (context, child) {
                  double value = 1.0;
                  if (_pageController.position.haveDimensions) {
                    value = _pageController.page! - index;
                    value = (1 - (value.abs() * 0.3)).clamp(0.85, 1.0);
                  }

                  return Center(
                    child: Transform.scale(
                      scale: Curves.easeOut.transform(value),
                      child: Container(
                        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(22),
                          boxShadow: [
                            BoxShadow(
                              color: colorScheme.shadow.withOpacity(0.08),
                              blurRadius: 12,
                              offset: const Offset(0, 6),
                            ),
                          ],
                          border: Border.all(
                            color: colorScheme.primary.withOpacity(0.2),
                            width: 2.0,
                          ),
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(20),
                          child: Stack(
                            children: [
                              Image.asset(
                                imageURL,
                                fit: BoxFit.cover,
                                width: double.infinity,
                                height: double.infinity,
                                errorBuilder: (_, __, ___) => Image.network(
                                  imageURL,
                                  fit: BoxFit.cover,
                                  width: double.infinity,
                                  height: double.infinity,
                                  errorBuilder: (_, __, ___) => const ColoredBox(
                                    color: Colors.black12,
                                    child: Center(child: Icon(Icons.image_not_supported)),
                                  ),
                                ),
                              ),
                              Positioned(
                                bottom: 0,
                                left: 0,
                                right: 0,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                  decoration: BoxDecoration(
                                    color: Colors.black.withOpacity(0.45),
                                    borderRadius: const BorderRadius.vertical(
                                      bottom: Radius.circular(20),
                                    ),
                                  ),
                                  child: Text(
                                    title,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 16,
                                      fontWeight: FontWeight.w600,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ),

        const SizedBox(height: 12),

        // ✅ Dot Indicator
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(items.length, (index) {
            final isSelected = _currentIndex == index;
            return AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              margin: const EdgeInsets.symmetric(horizontal: 4),
              height: 10,
              width: isSelected ? 22 : 10,
              decoration: BoxDecoration(
                color: isSelected
                    ? colorScheme.primary
                    : colorScheme.outline.withOpacity(0.4),
                borderRadius: BorderRadius.circular(20),
              ),
            );
          }),
        ),
      ],
    );
  }
}
