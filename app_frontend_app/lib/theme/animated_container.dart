import 'package:flutter/material.dart';

class AnimatedGradientContainer extends StatefulWidget {
  final Widget Function(BuildContext context, Alignment begin, Alignment end)
      builder;
  final Duration duration;

  const AnimatedGradientContainer({
    super.key,
    required this.builder,
    this.duration = const Duration(seconds: 6),
  });

  @override
  State<AnimatedGradientContainer> createState() =>
      _AnimatedGradientContainerState();
}

class _AnimatedGradientContainerState extends State<AnimatedGradientContainer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    )..repeat(reverse: true);

    _animation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOutSine,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        final value = _animation.value;
        final begin = Alignment(
          -1 + 2 * value,
          -1 + 0.5 * (1 - value),
        );
        final end = Alignment(
          1 - 2 * value,
          1 - 0.5 * (1 - value),
        );

        return widget.builder(context, begin, end);
      },
    );
  }
}
