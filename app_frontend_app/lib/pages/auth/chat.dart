import 'package:college_app/services/chat_api.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// ── ConversationsScreen ───────────────────────────────────────────────────────

class ConversationsScreen extends StatefulWidget {
  const ConversationsScreen({super.key});

  @override
  State<ConversationsScreen> createState() => _ConversationsScreenState();
}

class _ConversationsScreenState extends State<ConversationsScreen> {
  final ChatApi _api = ChatApi();
  late Future<List<Map<String, dynamic>>> _conversationsFuture;

  @override
  void initState() {
    super.initState();
    _conversationsFuture = _api.getConversations();
  }

  void _refresh() {
    setState(() {
      _conversationsFuture = _api.getConversations();
    });
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text('Messages', style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_square),
            tooltip: 'New conversation',
            onPressed: () => _showNewConversationSheet(context),
          ),
        ],
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _conversationsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Text(
                'Failed to load conversations',
                style: GoogleFonts.poppins(color: colorScheme.error),
              ),
            );
          }

          final conversations = snapshot.data ?? [];

          if (conversations.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.chat_bubble_outline_rounded,
                    size: 64,
                    color: colorScheme.onSurface.withAlpha(77),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No conversations yet.',
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Start one!',
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      color: colorScheme.onSurface.withAlpha(128),
                    ),
                  ),
                ],
              ),
            );
          }

          return ListView.separated(
            itemCount: conversations.length,
            separatorBuilder: (_, __) => const Divider(height: 1, indent: 72),
            itemBuilder: (context, index) {
              return _ConversationTile(
                data: conversations[index],
                onTap: () {
                  final id = conversations[index]['id'] as int;
                  final name = _conversationDisplayName(conversations[index]);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          ChatScreen(conversationId: id, conversationName: name),
                    ),
                  );
                },
              );
            },
          );
        },
      ),
    );
  }

  void _showNewConversationSheet(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _NewConversationSheet(
        api: _api,
        onCreated: (Map<String, dynamic> conv) {
          _refresh();
          final id = conv['id'] as int;
          final name = _conversationDisplayName(conv);
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) =>
                  ChatScreen(conversationId: id, conversationName: name),
            ),
          );
        },
      ),
    );
  }

  String _conversationDisplayName(Map<String, dynamic> conv) {
    final name = conv['name'] as String?;
    final type = conv['type'] as String?;
    if (name != null && name.isNotEmpty) return name;
    if (type == 'direct') return 'Direct Message';
    return 'Group Chat';
  }
}

// ── _ConversationTile ─────────────────────────────────────────────────────────

class _ConversationTile extends StatelessWidget {
  const _ConversationTile({required this.data, required this.onTap});

  final Map<String, dynamic> data;
  final VoidCallback onTap;

  String _displayName() {
    final name = data['name'] as String?;
    final type = data['type'] as String?;
    if (name != null && name.isNotEmpty) return name;
    if (type == 'direct') return 'Direct Message';
    return 'Group Chat';
  }

  String _subtitle() {
    final last = data['last_message'];
    if (last == null) return 'No messages yet';
    final content = last['content'] as String? ?? '';
    return content.isEmpty ? 'No messages yet' : content;
  }

  String _formattedTime() {
    final raw = data['created_at'] as String?;
    if (raw == null) return '';
    try {
      final dt = DateTime.parse(raw).toLocal();
      final now = DateTime.now();
      final isToday = dt.year == now.year &&
          dt.month == now.month &&
          dt.day == now.day;
      if (isToday) {
        final h = dt.hour.toString().padLeft(2, '0');
        final m = dt.minute.toString().padLeft(2, '0');
        return '$h:$m';
      }
      const months = [
        '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];
      return '${months[dt.month]} ${dt.day}';
    } catch (_) {
      return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final name = _displayName();
    final initial = name.isNotEmpty ? name[0].toUpperCase() : '?';

    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: CircleAvatar(
        backgroundColor: colorScheme.primary,
        child: Text(
          initial,
          style: GoogleFonts.poppins(
            color: colorScheme.onPrimary,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      title: Text(
        name,
        style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 15),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      subtitle: Text(
        _subtitle(),
        style: GoogleFonts.poppins(
          fontSize: 13,
          color: colorScheme.onSurface.withAlpha(153),
        ),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: Text(
        _formattedTime(),
        style: GoogleFonts.poppins(
          fontSize: 12,
          color: colorScheme.onSurface.withAlpha(102),
        ),
      ),
      onTap: onTap,
    );
  }
}

// ── _NewConversationSheet ─────────────────────────────────────────────────────

class _NewConversationSheet extends StatefulWidget {
  const _NewConversationSheet({required this.api, required this.onCreated});

  final ChatApi api;
  final void Function(Map<String, dynamic> conv) onCreated;

  @override
  State<_NewConversationSheet> createState() => _NewConversationSheetState();
}

class _NewConversationSheetState extends State<_NewConversationSheet> {
  final _uidController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _uidController.dispose();
    super.dispose();
  }

  Future<void> _startChat() async {
    final uid = _uidController.text.trim();
    if (uid.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a Firebase UID')),
      );
      return;
    }
    setState(() => _isLoading = true);
    try {
      final conv = await widget.api.createConversation(
        type: 'direct',
        memberUids: [uid],
      );
      if (!mounted) return;
      Navigator.pop(context); // close sheet
      widget.onCreated(conv);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Padding(
      padding: EdgeInsets.fromLTRB(24, 24, 24, 24 + bottomInset),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: colorScheme.onSurface.withAlpha(51),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'New Direct Message',
            style: GoogleFonts.poppins(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Enter the Firebase UID of the person you want to chat with.',
            style: GoogleFonts.poppins(
              fontSize: 13,
              color: colorScheme.onSurface.withAlpha(153),
            ),
          ),
          const SizedBox(height: 20),
          TextField(
            controller: _uidController,
            decoration: InputDecoration(
              labelText: 'Firebase UID',
              hintText: 'e.g. ItBpeviDV1XMpPVPD9J5...',
              prefixIcon: Icon(Icons.person_outline, color: colorScheme.primary),
            ),
            style: GoogleFonts.poppins(fontSize: 14),
            autofocus: true,
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: colorScheme.primary,
                foregroundColor: colorScheme.onPrimary,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onPressed: _isLoading ? null : _startChat,
              child: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : Text(
                      'Start Chat',
                      style:
                          GoogleFonts.poppins(fontWeight: FontWeight.w600),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── ChatScreen ────────────────────────────────────────────────────────────────

class ChatScreen extends StatefulWidget {
  final int conversationId;
  final String conversationName;

  const ChatScreen({
    super.key,
    required this.conversationId,
    required this.conversationName,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ChatApi _api = ChatApi();
  final List<Map<String, dynamic>> _messages = [];
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  bool _isLoading = true;
  bool _wsConnected = false;
  String _currentUid = '';

  @override
  void initState() {
    super.initState();
    _currentUid = FirebaseAuth.instance.currentUser?.uid ?? '';
    _init();
  }

  Future<void> _init() async {
    // Load history
    try {
      final msgs = await _api.getMessages(widget.conversationId);
      if (!mounted) return;
      setState(() {
        _messages.addAll(msgs);
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }

    // Connect WebSocket (no-op on Flutter Web — falls back to HTTP send)
    try {
      await _api.connectToConversation(
        widget.conversationId,
        onMessage: (msg) {
          if (!mounted) return;
          if (msg['type'] != 'system') {
            setState(() => _messages.add(msg));
            _scrollToBottom();
          }
        },
        onDisconnect: () {
          if (mounted) setState(() => _wsConnected = false);
        },
      );
      if (mounted) setState(() => _wsConnected = true);
    } catch (_) {
      // WebSocket unavailable (web platform or network issue) — HTTP fallback.
      if (mounted) setState(() => _wsConnected = false);
    }
  }

  @override
  void dispose() {
    _api.disconnect();
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    final content = _inputController.text.trim();
    if (content.isEmpty) return;
    _inputController.clear();

    try {
      if (_api.isConnected) {
        await _api.sendMessageWs(content);
        // Broadcast loop will add the echo from the server.
      } else {
        final msg = await _api.sendMessageHttp(
            widget.conversationId, content);
        if (mounted) {
          setState(() => _messages.add(msg));
          _scrollToBottom();
        }
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to send: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.conversationName,
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Icon(
              Icons.circle,
              size: 10,
              color: _wsConnected ? Colors.greenAccent : Colors.grey,
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _messages.isEmpty
                    ? Center(
                        child: Text(
                          'No messages yet. Say hello!',
                          style: GoogleFonts.poppins(
                            color: colorScheme.onSurface.withAlpha(128),
                          ),
                        ),
                      )
                    : ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 8),
                        itemCount: _messages.length,
                        itemBuilder: (context, index) => _MessageBubble(
                          message: _messages[index],
                          currentUid: _currentUid,
                        ),
                      ),
          ),
          _InputBar(
            controller: _inputController,
            onSend: _sendMessage,
          ),
        ],
      ),
    );
  }
}

// ── _MessageBubble ────────────────────────────────────────────────────────────

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({
    required this.message,
    required this.currentUid,
  });

  final Map<String, dynamic> message;
  final String currentUid;

  String _formattedTime() {
    final raw = message['created_at'] as String?;
    if (raw == null) return '';
    try {
      final dt = DateTime.parse(raw).toLocal();
      final h = dt.hour.toString().padLeft(2, '0');
      final m = dt.minute.toString().padLeft(2, '0');
      return '$h:$m';
    } catch (_) {
      return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    final isSent = (message['sender_uid'] as String?) == currentUid;
    final content = (message['content'] as String?) ?? '';
    final displayName = message['display_name'] as String?;
    final maxWidth = MediaQuery.of(context).size.width * 0.7;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Align(
        alignment: isSent ? Alignment.centerRight : Alignment.centerLeft,
        child: ConstrainedBox(
          constraints: BoxConstraints(maxWidth: maxWidth),
          child: Column(
            crossAxisAlignment:
                isSent ? CrossAxisAlignment.end : CrossAxisAlignment.start,
            children: [
              // Sender name (received messages only)
              if (!isSent && displayName != null && displayName.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(left: 4, bottom: 2),
                  child: Text(
                    displayName,
                    style: GoogleFonts.poppins(
                      fontSize: 11,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),

              // Bubble
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: isSent ? Colors.blue[600] : Colors.grey[200],
                  borderRadius: BorderRadius.only(
                    topLeft: const Radius.circular(16),
                    topRight: const Radius.circular(16),
                    bottomLeft: isSent
                        ? const Radius.circular(16)
                        : const Radius.circular(4),
                    bottomRight: isSent
                        ? const Radius.circular(4)
                        : const Radius.circular(16),
                  ),
                ),
                child: Text(
                  content,
                  style: GoogleFonts.poppins(
                    fontSize: 14,
                    color: isSent ? Colors.white : Colors.black87,
                  ),
                ),
              ),

              // Timestamp
              Padding(
                padding: const EdgeInsets.only(top: 2, left: 4, right: 4),
                child: Text(
                  _formattedTime(),
                  style: GoogleFonts.poppins(
                    fontSize: 10,
                    color: Colors.grey[500],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── _InputBar ─────────────────────────────────────────────────────────────────

class _InputBar extends StatelessWidget {
  const _InputBar({required this.controller, required this.onSend});

  final TextEditingController controller;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return SafeArea(
      child: Container(
        decoration: BoxDecoration(
          color: colorScheme.surface,
          border: Border(
            top: BorderSide(
              color: colorScheme.onSurface.withAlpha(26),
            ),
          ),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                minLines: 1,
                maxLines: 4,
                textCapitalization: TextCapitalization.sentences,
                decoration: InputDecoration(
                  hintText: 'Type a message...',
                  hintStyle: GoogleFonts.poppins(
                      fontSize: 14, color: Colors.grey[400]),
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 10),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: colorScheme.onSurface.withAlpha(13),
                ),
                style: GoogleFonts.poppins(fontSize: 14),
                onSubmitted: (_) => onSend(),
              ),
            ),
            const SizedBox(width: 8),
            Material(
              color: Colors.blue[600],
              shape: const CircleBorder(),
              child: InkWell(
                customBorder: const CircleBorder(),
                onTap: onSend,
                child: const Padding(
                  padding: EdgeInsets.all(10),
                  child: Icon(Icons.send, color: Colors.white, size: 20),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
