// DEBUG BAR — dev-only UI strip, to be deleted before production release.
// Provides quick endpoint testing buttons grouped by category.
// Collapsed by default; tap the header to expand via AnimatedCrossFade.

import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mime/mime.dart';

import 'package:college_app/config/api_config.dart';

// ── Auth helpers ──────────────────────────────────────────────────────────────

Future<String> _token() async {
  final user = FirebaseAuth.instance.currentUser;
  return await user?.getIdToken() ?? '';
}

Map<String, String> _authJson(String token) => {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };

// ── Pretty-print ──────────────────────────────────────────────────────────────

String _pretty(String raw) {
  try {
    return const JsonEncoder.withIndent('  ').convert(jsonDecode(raw));
  } catch (_) {
    return raw;
  }
}

// ── Result bottom sheet ───────────────────────────────────────────────────────

void _showResultSheet(BuildContext context, String body,
    {required bool isError}) {
  showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => DraggableScrollableSheet(
      initialChildSize: 0.45,
      maxChildSize: 0.8,
      minChildSize: 0.2,
      expand: false,
      builder: (_, controller) => Container(
        decoration: BoxDecoration(
          color: isError ? Colors.red.shade900 : Colors.green.shade900,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
        ),
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36,
                height: 4,
                margin: const EdgeInsets.only(bottom: 10),
                decoration: BoxDecoration(
                  color: Colors.white38,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                controller: controller,
                child: SelectableText(
                  _pretty(body),
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 12,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 10),
            Center(
              child: OutlinedButton(
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white38),
                ),
                onPressed: () => Navigator.pop(context),
                child: const Text('Close'),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

// ── Request runners ───────────────────────────────────────────────────────────

Future<void> _get(
  BuildContext ctx,
  String path, {
  bool auth = false,
  Map<String, String>? query,
}) async {
  final t = auth ? await _token() : '';
  Uri uri = ApiConfig.endpoint(path);
  if (query != null) {
    uri = uri.replace(queryParameters: {...uri.queryParameters, ...query});
  }
  try {
    final res = await http
        .get(uri, headers: auth && t.isNotEmpty ? _authJson(t) : {})
        .timeout(const Duration(seconds: 15));
    if (!ctx.mounted) return;
    _showResultSheet(ctx, res.body, isError: res.statusCode >= 400);
  } catch (e) {
    if (!ctx.mounted) return;
    _showResultSheet(ctx, 'Exception: $e', isError: true);
  }
}

Future<void> _post(
  BuildContext ctx,
  String path,
  Map<String, dynamic> payload, {
  bool auth = true,
}) async {
  final t = auth ? await _token() : '';
  try {
    final res = await http
        .post(
          ApiConfig.endpoint(path),
          headers: auth && t.isNotEmpty
              ? _authJson(t)
              : {'Content-Type': 'application/json'},
          body: jsonEncode(payload),
        )
        .timeout(const Duration(seconds: 15));
    if (!ctx.mounted) return;
    _showResultSheet(ctx, res.body, isError: res.statusCode >= 400);
  } catch (e) {
    if (!ctx.mounted) return;
    _showResultSheet(ctx, 'Exception: $e', isError: true);
  }
}

// ── Verify dialog ─────────────────────────────────────────────────────────────

Future<void> _verify(BuildContext ctx) async {
  final idCtrl = TextEditingController();
  final actionCtrl = TextEditingController(text: 'approve');

  final ok = await showDialog<bool>(
    context: ctx,
    builder: (_) => AlertDialog(
      title: const Text('Verify Club'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: idCtrl,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(
                labelText: 'Club ID', hintText: '1'),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: actionCtrl,
            decoration: const InputDecoration(
                labelText: 'Action', hintText: 'approve / reject'),
          ),
        ],
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel')),
        ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Send')),
      ],
    ),
  );

  if (ok != true || !ctx.mounted) return;
  final clubId = idCtrl.text.trim();
  final action = actionCtrl.text.trim();
  if (clubId.isEmpty) {
    _showResultSheet(ctx, 'Club ID is required', isError: true);
    return;
  }
  await _post(ctx, '/clubs/$clubId/verify', {'action': action});
}

// ── Media upload (XFile — web-compatible) ────────────────────────────────────

Future<void> _uploadMedia(BuildContext ctx) async {
  final t = await _token();
  if (t.isEmpty) {
    _showResultSheet(ctx, 'Not authenticated', isError: true);
    return;
  }

  final picker = ImagePicker();
  final xfile = await picker.pickImage(source: ImageSource.gallery);
  if (xfile == null) return;
  if (!ctx.mounted) return;

  final bytes = await xfile.readAsBytes();
  final mimeType = lookupMimeType(xfile.name) ?? 'image/jpeg';

  final request =
      http.MultipartRequest('POST', ApiConfig.endpoint('/media/upload'));
  request.headers['Authorization'] = 'Bearer $t';
  request.files.add(http.MultipartFile.fromBytes(
    'image',
    bytes,
    filename: xfile.name,
    contentType: MediaType.parse(mimeType),
  ));

  try {
    final streamed =
        await request.send().timeout(const Duration(seconds: 30));
    final body = await streamed.stream.bytesToString();
    if (!ctx.mounted) return;
    _showResultSheet(ctx, body, isError: streamed.statusCode >= 400);
  } catch (e) {
    if (!ctx.mounted) return;
    _showResultSheet(ctx, 'Exception: $e', isError: true);
  }
}

// ── DebugBar widget ───────────────────────────────────────────────────────────

class DebugBar extends StatefulWidget {
  const DebugBar({super.key});

  @override
  State<DebugBar> createState() => _DebugBarState();
}

class _DebugBarState extends State<DebugBar> {
  bool _expanded = false;
  final Set<String> _busy = {};

  void _setBusy(String k, bool v) {
    if (mounted) setState(() => v ? _busy.add(k) : _busy.remove(k));
  }

  Future<void> _run(String k, Future<void> Function() fn) async {
    _setBusy(k, true);
    try {
      await fn();
    } finally {
      _setBusy(k, false);
    }
  }

  Widget _btn(String label, String key, Future<void> Function() fn) {
    final loading = _busy.contains(key);
    return Padding(
      padding: const EdgeInsets.only(right: 6, bottom: 6),
      child: OutlinedButton(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          minimumSize: Size.zero,
          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          textStyle: const TextStyle(fontSize: 11),
          side: const BorderSide(color: Colors.white30),
          foregroundColor: Colors.white70,
        ),
        onPressed: loading ? null : () => _run(key, fn),
        child: loading
            ? const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                    strokeWidth: 1.5, color: Colors.white54))
            : Text(label),
      ),
    );
  }

  Widget _section(String title, List<Widget> buttons) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: Colors.white12, height: 12),
        Text(
          title,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: Colors.white38,
            letterSpacing: 1.1,
          ),
        ),
        const SizedBox(height: 6),
        Wrap(children: buttons),
      ],
    );
  }

  Widget _expandedContent() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // PROFILE
          _section('PROFILE', [
            _btn('GET /profiles/me', 'profile_get',
                () => _get(context, '/profiles/me', auth: true)),
            _btn('POST /profiles/me', 'profile_update',
                () => _post(context, '/profiles/me', {
                      'name': 'Debug User',
                      'college': 'NIT Agartala',
                      'year_of_graduation': '2027',
                      'branch': 'Computer Science and Engineering',
                      'avatar_url':
                          'https://cdn-icons-png.flaticon.com/512/847/847969.png',
                      'latitude': 'Not specified',
                      'longitude': 'Not specified',
                    })),
          ]),

          // EVENTS
          _section('EVENTS', [
            _btn('GET ongoing', 'events_ongoing',
                () => _get(context, '/events',
                    query: {'status': 'ongoing'})),
            _btn('GET upcoming', 'events_upcoming',
                () => _get(context, '/events',
                    query: {'status': 'upcoming'})),
            _btn('POST /events', 'events_post',
                () => _post(context, '/events', {
                      'title': 'Test Event',
                      'status': 'upcoming',
                      'starts_at': '2026-04-01T10:00:00Z',
                    })),
          ]),

          // CLUBS
          _section('CLUBS', [
            _btn('GET /clubs', 'clubs_list',
                () => _get(context, '/clubs')),
            _btn('GET /clubs/pending', 'clubs_pending',
                () => _get(context, '/clubs/pending', auth: true)),
            _btn('POST /clubs/register', 'clubs_register',
                () => _post(context, '/clubs/register', {
                      'club_name': 'Debug Club',
                      'parent_college': 'NIT Agartala',
                      'description': 'Test club reg',
                      'members': <dynamic>[],
                      'account_manager_uid': '',
                      'document_url': '',
                    })),
            _btn('POST /clubs/{id}/verify', 'clubs_verify',
                () => _verify(context)),
            _btn('GET /clubs/{id}', 'clubs_single',
                () async {
                  final idCtrl = TextEditingController();
                  final ok = await showDialog<bool>(
                    context: context,
                    builder: (_) => AlertDialog(
                      title: const Text('Get Club'),
                      content: TextField(
                        controller: idCtrl,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                            labelText: 'Club ID', hintText: '1'),
                      ),
                      actions: [
                        TextButton(
                            onPressed: () => Navigator.pop(context, false),
                            child: const Text('Cancel')),
                        ElevatedButton(
                            onPressed: () => Navigator.pop(context, true),
                            child: const Text('Get')),
                      ],
                    ),
                  );
                  if (ok != true || !context.mounted) return;
                  final id = idCtrl.text.trim();
                  if (id.isEmpty) return;
                  await _get(context, '/clubs/$id');
                }),
            _btn('GET /clubs/{id}/members', 'clubs_members',
                () async {
                  final idCtrl = TextEditingController();
                  final ok = await showDialog<bool>(
                    context: context,
                    builder: (_) => AlertDialog(
                      title: const Text('Get Club Members'),
                      content: TextField(
                        controller: idCtrl,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                            labelText: 'Club ID', hintText: '1'),
                      ),
                      actions: [
                        TextButton(
                            onPressed: () => Navigator.pop(context, false),
                            child: const Text('Cancel')),
                        ElevatedButton(
                            onPressed: () => Navigator.pop(context, true),
                            child: const Text('Get')),
                      ],
                    ),
                  );
                  if (ok != true || !context.mounted) return;
                  final id = idCtrl.text.trim();
                  if (id.isEmpty) return;
                  await _get(context, '/clubs/$id/members');
                }),
          ]),

          // MEDIA
          _section('MEDIA', [
            _btn('POST /media/upload', 'media_upload',
                () => _uploadMedia(context)),
          ]),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFF1A1A1A),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header (always visible) ──────────────────────────────────
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            child: Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                children: [
                  const Icon(Icons.build, size: 13, color: Colors.grey),
                  const SizedBox(width: 6),
                  const Text(
                    '🛠 DEBUG',
                    style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5),
                  ),
                  const Spacer(),
                  Icon(
                    _expanded
                        ? Icons.keyboard_arrow_up
                        : Icons.keyboard_arrow_down,
                    color: Colors.grey,
                    size: 18,
                  ),
                ],
              ),
            ),
          ),

          // ── Animated expand / collapse ───────────────────────────────
          AnimatedCrossFade(
            firstChild: const SizedBox.shrink(),
            secondChild: _expandedContent(),
            crossFadeState: _expanded
                ? CrossFadeState.showSecond
                : CrossFadeState.showFirst,
            duration: const Duration(milliseconds: 200),
          ),
        ],
      ),
    );
  }
}
