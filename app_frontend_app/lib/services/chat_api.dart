// ignore_for_file: avoid_print
import 'dart:async';
import 'dart:convert';
import 'dart:io' show WebSocket; // dart:io WebSocket — works on Android/iOS/desktop.
// NOTE: dart:io is NOT available on Flutter Web. When running on Chrome
// (e.g. `flutter run -d chrome`), the WebSocket methods (connectToConversation,
// sendMessageWs) will throw at runtime. All REST methods (getConversations,
// createConversation, getMessages, sendMessageHttp) work on every platform.
// To add web support later, swap dart:io WebSocket for the `web_socket_channel`
// package: https://pub.dev/packages/web_socket_channel

import 'package:college_app/config/api_config.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;

class ChatApi {
  // ── Internal state ─────────────────────────────────────────────────────────

  WebSocket? _socket;
  StreamSubscription<dynamic>? _socketSub;
  bool _connected = false;

  // ── Auth helper ────────────────────────────────────────────────────────────

  Future<String?> _getToken() async {
    return await FirebaseAuth.instance.currentUser?.getIdToken();
  }

  Map<String, String> _authHeaders(String token) => {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };

  // ── WebSocket URL helper ───────────────────────────────────────────────────

  /// Converts the HTTP base URL to its WebSocket equivalent.
  /// http://host  → ws://host
  /// https://host → wss://host
  String _wsBase() {
    final base = ApiConfig.baseUrl;
    if (base.startsWith('https://')) {
      return base.replaceFirst('https://', 'wss://');
    }
    return base.replaceFirst('http://', 'ws://');
  }

  // ── REST: conversations ────────────────────────────────────────────────────

  /// GET /api/v1/chat/conversations
  /// Returns the caller's conversation list ordered by latest activity.
  Future<List<Map<String, dynamic>>> getConversations() async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final res = await http
        .get(
          ApiConfig.endpoint('/chat/conversations'),
          headers: _authHeaders(token),
        )
        .timeout(const Duration(seconds: 15));

    if (res.statusCode != 200) {
      throw Exception('getConversations failed: ${res.statusCode} ${res.body}');
    }
    return List<Map<String, dynamic>>.from(jsonDecode(res.body) as List);
  }

  /// POST /api/v1/chat/conversations
  /// Creates a new conversation and returns the ConversationDetailResponse.
  Future<Map<String, dynamic>> createConversation({
    required String type,
    required List<String> memberUids,
    String? name,
    bool isAnonymous = false,
  }) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final body = <String, dynamic>{
      'type': type,
      'member_uids': memberUids,
      if (name != null) 'name': name,
      'is_anonymous': isAnonymous,
    };

    final res = await http
        .post(
          ApiConfig.endpoint('/chat/conversations'),
          headers: _authHeaders(token),
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 15));

    if (res.statusCode != 201) {
      throw Exception(
          'createConversation failed: ${res.statusCode} ${res.body}');
    }
    return Map<String, dynamic>.from(jsonDecode(res.body) as Map);
  }

  // ── REST: messages ─────────────────────────────────────────────────────────

  /// GET /api/v1/chat/conversations/{id}/messages
  /// Returns messages in ascending order (oldest first).
  /// Pass [beforeId] for cursor-based pagination (load older messages).
  Future<List<Map<String, dynamic>>> getMessages(
    int conversationId, {
    int limit = 50,
    int? beforeId,
  }) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final query = <String, String>{'limit': '$limit'};
    if (beforeId != null) query['before_id'] = '$beforeId';

    final uri = ApiConfig.endpoint('/chat/conversations/$conversationId/messages')
        .replace(queryParameters: query);

    final res = await http
        .get(uri, headers: _authHeaders(token))
        .timeout(const Duration(seconds: 15));

    if (res.statusCode != 200) {
      throw Exception('getMessages failed: ${res.statusCode} ${res.body}');
    }
    return List<Map<String, dynamic>>.from(jsonDecode(res.body) as List);
  }

  /// POST /api/v1/chat/conversations/{id}/messages
  /// HTTP fallback for sending a message when the WebSocket is not connected.
  Future<Map<String, dynamic>> sendMessageHttp(
    int conversationId,
    String content, {
    String messageType = 'text',
  }) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final res = await http
        .post(
          ApiConfig.endpoint('/chat/conversations/$conversationId/messages'),
          headers: _authHeaders(token),
          body: jsonEncode({'content': content, 'message_type': messageType}),
        )
        .timeout(const Duration(seconds: 15));

    if (res.statusCode != 201) {
      throw Exception('sendMessageHttp failed: ${res.statusCode} ${res.body}');
    }
    return Map<String, dynamic>.from(jsonDecode(res.body) as Map);
  }

  // ── WebSocket ──────────────────────────────────────────────────────────────

  /// Connect to /ws/chat/{conversationId}?token=<firebase_token>.
  ///
  /// - [onMessage] is called for every JSON frame received from the server.
  /// - [onDisconnect] is called when the connection closes (normally or on error).
  ///
  /// Throws if a token cannot be retrieved or the connection fails.
  ///
  /// NOTE: Only works on Android / iOS / desktop. Throws on Flutter Web
  /// because dart:io is unavailable in browser environments.
  Future<void> connectToConversation(
    int conversationId, {
    required void Function(Map<String, dynamic> message) onMessage,
    required void Function() onDisconnect,
  }) async {
    // Disconnect any existing socket first.
    disconnect();

    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final wsUrl =
        '${_wsBase()}/ws/chat/$conversationId?token=${Uri.encodeComponent(token)}';

    _socket = await WebSocket.connect(wsUrl);
    _connected = true;

    _socketSub = _socket!.listen(
      (dynamic rawFrame) {
        if (rawFrame is String) {
          try {
            final decoded = jsonDecode(rawFrame);
            if (decoded is Map<String, dynamic>) {
              onMessage(decoded);
            }
          } catch (e) {
            print('ChatApi: failed to decode WS frame: $e');
          }
        }
      },
      onDone: () {
        _connected = false;
        onDisconnect();
      },
      onError: (Object err) {
        print('ChatApi: WebSocket error: $err');
        _connected = false;
        onDisconnect();
      },
      cancelOnError: true,
    );
  }

  /// Send a text message over the open WebSocket.
  /// Falls back silently if the socket is not connected — callers should
  /// check [isConnected] and use [sendMessageHttp] as a fallback if needed.
  Future<void> sendMessageWs(
    String content, {
    String messageType = 'text',
  }) async {
    if (_socket == null || !_connected) {
      throw Exception('WebSocket is not connected');
    }
    _socket!.add(jsonEncode({
      'content': content,
      'message_type': messageType,
    }));
  }

  /// Whether the WebSocket is currently open.
  bool get isConnected => _connected && _socket != null;

  /// Close the WebSocket connection and clean up listeners.
  void disconnect() {
    _socketSub?.cancel();
    _socketSub = null;
    _socket?.close();
    _socket = null;
    _connected = false;
  }
}
