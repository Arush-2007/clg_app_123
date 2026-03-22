import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:college_app/config/api_config.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mime/mime.dart';


class ImageAndDataUploader {
  final ImagePicker _picker = ImagePicker();
  File? selectedImage;

  /// Picks image from gallery and stores in `selectedImage`.
  Future<bool> pickImage() async {
    try {
      final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
      if (pickedFile != null) {
        selectedImage = File(pickedFile.path);
        return true;
      }
      return false;
    } catch (e) {
      debugPrint("Image picking failed: $e");
      return false;
    }
  }

  Future<String?> uploadImage({
    required BuildContext context,
    required String token,
  }) async {
    if (selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select an image first.'),
          backgroundColor: Colors.red,
        ),
      );
      return null;
    }

    final uri = ApiConfig.endpoint('/media/upload');
    final request = http.MultipartRequest("POST", uri);
    request.headers["Authorization"] = "Bearer $token";

    final mimeType = lookupMimeType(selectedImage!.path);
    final imageFile = await http.MultipartFile.fromPath(
      'image', // expected field name
      selectedImage!.path,
      contentType: mimeType != null ? MediaType.parse(mimeType) : null,
    );

    request.files.add(imageFile);
    try {
      final response = await request.send();
      if (response.statusCode >= 200 && response.statusCode < 300) {
        final body = await response.stream.bytesToString();
        final decoded = jsonDecode(body.isEmpty ? '{}' : body);
        return decoded['imageUrl']?.toString();
      }
      return null;
    } catch (e) {
      // ignore: use_build_context_synchronously
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Upload failed: $e'), backgroundColor: Colors.red),
      );
      return null;
    }
  }

  Future<http.Response> submitProfile({
    required String token,
    required Map<String, dynamic> body,
  }) {
    return http.post(
      ApiConfig.endpoint('/profiles/me'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(body),
    ).timeout(const Duration(seconds: 12));
  }
}