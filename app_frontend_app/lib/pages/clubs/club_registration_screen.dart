import 'dart:convert';

import 'package:college_app/config/api_config.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class ClubRegistrationScreen extends StatefulWidget {
  const ClubRegistrationScreen({super.key});

  @override
  State<ClubRegistrationScreen> createState() => _ClubRegistrationScreenState();
}

class _ClubRegistrationScreenState extends State<ClubRegistrationScreen> {
  final _clubNameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _documentUrlController = TextEditingController();
  final _accountManagerController = TextEditingController();

  // Member input row controllers
  final _memberUidController = TextEditingController();
  final _memberPositionController = TextEditingController();
  final _memberHierarchyController = TextEditingController();

  final List<Map<String, dynamic>> _members = [];
  bool _isLoading = false;

  @override
  void dispose() {
    _clubNameController.dispose();
    _descriptionController.dispose();
    _documentUrlController.dispose();
    _accountManagerController.dispose();
    _memberUidController.dispose();
    _memberPositionController.dispose();
    _memberHierarchyController.dispose();
    super.dispose();
  }

  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
      ),
    );
  }

  void _addMember() {
    final uid = _memberUidController.text.trim();
    final position = _memberPositionController.text.trim();
    final hierarchyRaw = _memberHierarchyController.text.trim();

    if (uid.isEmpty || position.isEmpty || hierarchyRaw.isEmpty) {
      _showSnackBar('Fill UID, position, and hierarchy before adding.',
          isError: true);
      return;
    }
    final hierarchy = int.tryParse(hierarchyRaw);
    if (hierarchy == null) {
      _showSnackBar('Hierarchy must be a number.', isError: true);
      return;
    }

    setState(() {
      _members.add({
        'firebase_uid': uid,
        'position_name': position,
        'hierarchy': hierarchy,
      });
      _memberUidController.clear();
      _memberPositionController.clear();
      _memberHierarchyController.clear();
    });
  }

  void _removeMember(int index) {
    setState(() => _members.removeAt(index));
  }

  bool _validate() {
    if (_clubNameController.text.trim().isEmpty) {
      _showSnackBar('Club name is required.', isError: true);
      return false;
    }
    if (_descriptionController.text.trim().length < 10) {
      _showSnackBar('Description must be at least 10 characters.', isError: true);
      return false;
    }
    if (_documentUrlController.text.trim().isEmpty) {
      _showSnackBar('Document URL is required.', isError: true);
      return false;
    }
    if (_accountManagerController.text.trim().isEmpty) {
      _showSnackBar('Account manager UID is required.', isError: true);
      return false;
    }
    if (_members.isEmpty) {
      _showSnackBar('Add at least one member.', isError: true);
      return false;
    }
    return true;
  }

  Future<void> _submitRegistration() async {
    if (!_validate()) return;

    setState(() => _isLoading = true);
    try {
      final user = FirebaseAuth.instance.currentUser;
      final token = await user?.getIdToken() ?? '';

      final response = await http
          .post(
            ApiConfig.endpoint('/clubs/register'),
            headers: {
              'Authorization': 'Bearer $token',
              'Content-Type': 'application/json',
            },
            body: jsonEncode({
              'club_name': _clubNameController.text.trim(),
              'parent_college': 'NIT Agartala',
              'description': _descriptionController.text.trim(),
              'document_url': _documentUrlController.text.trim(),
              'account_manager_uid': _accountManagerController.text.trim(),
              'members': _members,
            }),
          )
          .timeout(const Duration(seconds: 15));

      if (!mounted) return;

      if (response.statusCode >= 200 && response.statusCode < 300) {
        _showSnackBar('Club registration submitted!');
        Navigator.pop(context);
      } else {
        _showSnackBar(
          'Error ${response.statusCode}: ${response.body}',
          isError: true,
        );
      }
    } catch (e) {
      if (mounted) _showSnackBar('Request failed: $e', isError: true);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Register a Club')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Club Name ───────────────────────────────────────────────
            TextField(
              controller: _clubNameController,
              decoration: const InputDecoration(
                labelText: 'Club Name *',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),

            // ── Description ─────────────────────────────────────────────
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description *',
                border: OutlineInputBorder(),
              ),
              minLines: 3,
              maxLines: 5,
            ),
            const SizedBox(height: 16),

            // ── Document URL ─────────────────────────────────────────────
            TextField(
              controller: _documentUrlController,
              decoration: const InputDecoration(
                labelText: 'Document URL *',
                hintText: 'Paste document URL (Google Drive, etc.)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),

            // ── Account Manager UID ──────────────────────────────────────
            TextField(
              controller: _accountManagerController,
              decoration: const InputDecoration(
                labelText: 'Account Manager UID *',
                hintText: 'Firebase UID of member who manages club account',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),

            // ── Members Section ──────────────────────────────────────────
            const Text(
              'Members',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),

            if (_members.isNotEmpty)
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _members.length,
                itemBuilder: (_, i) {
                  final m = _members[i];
                  return ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: Text(m['firebase_uid'] as String),
                    subtitle: Text(
                        '${m['position_name']} (hierarchy: ${m['hierarchy']})'),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      onPressed: () => _removeMember(i),
                    ),
                  );
                },
              ),

            // Member input row
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: TextField(
                    controller: _memberUidController,
                    decoration: const InputDecoration(
                      labelText: 'UID',
                      border: OutlineInputBorder(),
                      contentPadding:
                          EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: TextField(
                    controller: _memberPositionController,
                    decoration: const InputDecoration(
                      labelText: 'Position',
                      border: OutlineInputBorder(),
                      contentPadding:
                          EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                SizedBox(
                  width: 60,
                  child: TextField(
                    controller: _memberHierarchyController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Hier.',
                      border: OutlineInputBorder(),
                      contentPadding:
                          EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                    ),
                  ),
                ),
              ],
            ),
            TextButton(
              onPressed: _addMember,
              child: const Text('+ Add Member'),
            ),

            const SizedBox(height: 24),

            // ── Submit ───────────────────────────────────────────────────
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _submitRegistration,
                child: _isLoading
                    ? const SizedBox(
                        height: 18,
                        width: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Register Club'),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
