import 'package:college_app/services/location.dart';
import 'package:college_app/services/ui_services/bottomBar.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:college_app/theme/theme.dart';
import 'package:college_app/services/image_data_picker.dart';
import 'dart:convert';

class ProfileSetupScreen extends StatefulWidget {
  const ProfileSetupScreen({super.key});

  @override
  State<ProfileSetupScreen> createState() => _ProfileSetupScreenState();
}

class _ProfileSetupScreenState extends State<ProfileSetupScreen> {

  // Controllers and uploader instance
  final TextEditingController _nameController = TextEditingController();
  final uploader = ImageAndDataUploader();

  static const String defaultAvatarUrl =
      'https://cdn-icons-png.flaticon.com/512/847/847969.png';

  String? selectedCollege = "NIT Agartala";
  String? selectedYear;
  String? selectedBranch;
  Map<String, String> location = {}; // to store location data
  bool isLoading = false;

  final List<String> graduationYears =
      List.generate(5, (i) => (2025 + i).toString());

  final List<String> branches = [
    'Computer Science and Engineering',
    'Electronics and Communication Engineering',
    'Electrical Engineering',
    'Mechanical Engineering',
    'Production Engineering',
    'Civil Engineering',
    'Chemical Engineering',
    'Biotechnology',
    'BSC - MSC - Physics',
    'BSC - MSC - Chemistry',
    'BSC - MSC - Mathematics',
    'BTech - MTech',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> submitProfile() async {

    if (isLoading) return; // Prevent multiple submissions


    final user = FirebaseAuth.instance.currentUser;

    if (user == null) {
      _showSnackBar("User not logged in.", isError: true);
      return;
    }

    if (_nameController.text.trim().isEmpty ||
        selectedCollege == null ||
        selectedYear == null ||
        selectedBranch == null) {
      _showSnackBar("Please complete all fields.", isError: true);
      return;
    }

    setState(() => isLoading = true);

    // attaching location to profile — never block submit on location failure
    try {
      location = await Location().getCoordinatesAndSave();
    } catch (_) {
      // location failed silently — continue with submit
      location = {};
    }
    if (location.containsKey('error')) {
      location = {};
    }

    final token = await user.getIdToken();
    if (token == null) {
      setState(() => isLoading = false);
      _showSnackBar("Failed to fetch auth token.", isError: true);
      return;
    }

    String imageUrl = defaultAvatarUrl;

    // Upload image first (if selected)
    if (uploader.selectedImage != null) {
      final uploadedUrl = await uploader.uploadImage(
        context: context,
        token: token,
      );

      if (uploadedUrl == null || uploadedUrl.isEmpty) {
        setState(() => isLoading = false);
        _showSnackBar("Image upload failed.", isError: true);
        return;
      }
      imageUrl = uploadedUrl;
    }

    final profileResponse = await uploader.submitProfile(
      token: token,
      body: {
        "name": _nameController.text.trim(),
        "college": selectedCollege!,
        "year_of_graduation": selectedYear!,
        "branch": selectedBranch!,
        "avatar_url": imageUrl,
        "latitude": location['latitude'] ?? "Not specified",
        "longitude": location['longitude'] ?? "Not specified",
      }
    );

    setState(() => isLoading = false);

    if (profileResponse.statusCode == 200) {
      _showSnackBar("Profile uploaded successfully!", isError: false);
      if (!mounted) return;
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const Bottombar()),
        (route) => false,
      );
    } else {
      String message = "Upload failed: ${profileResponse.statusCode}";
      try {
        final decoded = jsonDecode(profileResponse.body);
        if (decoded is Map && decoded["detail"] != null) {
          message = "Upload failed: ${decoded["detail"]}";
        }
      } catch (_) {}
      _showSnackBar(message, isError: true);
    }
  }

  void _showSnackBar(String message, {required bool isError}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : fireColor,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(80),
        child: AppBar(
          elevation: 12,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(bottom: Radius.circular(30)),
          ),
          shadowColor: Colors.black.withAlpha(isDark ? 100 : 60),
          title: const Text("Setup Profile",
              style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)),
          centerTitle: true,
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 140, 20, 120),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(child: _buildProfileImage()),
            const SizedBox(height: 40),
            _buildSection("Full Name", _buildTextField(_nameController, "Enter your name")),
            const SizedBox(height: 24),
            _buildSection("College", _buildDropdown(
              selectedCollege,
              const ['NIT Agartala'],
              (val) => setState(() => selectedCollege = val),
              label: "Select College",
            )),
            const SizedBox(height: 24),
            _buildSection("Graduation Year", _buildDropdown(
              selectedYear,
              graduationYears,
              (val) => setState(() => selectedYear = val),
              label: "Select Year",
            )),
            const SizedBox(height: 24),
            _buildSection("Branch", _buildDropdown(
              selectedBranch,
              branches,
              (val) => setState(() => selectedBranch = val),
              label: "Select Branch",
            )),
          ],
        ),
      ),
      bottomNavigationBar: _buildBottomBar(isDark),
    );
  }

  Widget _buildProfileImage() {
    return Stack(
      alignment: Alignment.bottomRight,
      children: [
        GestureDetector(
          onTap: () async {
            await uploader.pickImage();
            setState(() {});
          },
          child: Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: fireColor, width: 3),
            ),
            child: CircleAvatar(
              radius: 75,
              backgroundColor: fireAccent.withAlpha(30),
              backgroundImage: uploader.selectedImage != null
                  ? FileImage(uploader.selectedImage!)
                  : const NetworkImage(defaultAvatarUrl) as ImageProvider,
            ),
          ),
        ),
        Positioned(
          bottom: 6,
          right: 6,
          child: CircleAvatar(
            radius: 22,
            backgroundColor: fireColor,
            child: const Icon(Icons.add, color: Colors.white, size: 22),
          ),
        ),
      ],
    );
  }

  Widget _buildTextField(TextEditingController controller, String hint) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(
        hintText: hint,
        prefixIcon: const Icon(Icons.person_outline),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  Widget _buildDropdown(
    String? value,
    List<String> items,
    void Function(String?) onChanged, {
    required String label,
  }) {
    return DropdownButtonFormField<String>(
      value: value,
      isExpanded: true,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: const Icon(Icons.school),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
      items: items.map((e) {
        return DropdownMenuItem<String>(
          value: e,
          child: Text(
            e,
            overflow: TextOverflow.ellipsis,
            maxLines: 1,
            style: const TextStyle(fontSize: 14),
          ),
        );
      }).toList(),
      onChanged: onChanged,
    );
  }

  Widget _buildSection(String title, Widget child) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: GoogleFonts.poppins(
            fontSize: 18,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 8),
        child,
      ],
    );
  }

  Widget _buildBottomBar(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(30)),
        boxShadow: [
          BoxShadow(
            color: isDark ? Colors.white12 : Colors.black26,
            blurRadius: 18,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: isLoading ? null : submitProfile,
        style: ElevatedButton.styleFrom(
          backgroundColor: fireColor,
          padding: const EdgeInsets.symmetric(vertical: 18),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        child: isLoading
            ? const CircularProgressIndicator(color: Colors.white)
            : const Text("Submit Profile", style: TextStyle(fontSize: 18, color: Colors.white)),
      ),
    );
  }
}
