import 'dart:io';
import 'package:flutter/material.dart';
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

  /// Uploads selected image to the given endpoint with additional form fields
  Future<http.StreamedResponse?> uploadImageToAPI({
    required String endpoint,
    required Map<String, String> fields,
    required BuildContext context,
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

    final uri = Uri.parse(endpoint);
    final request = http.MultipartRequest("POST", uri);

    final mimeType = lookupMimeType(selectedImage!.path);
    final imageFile = await http.MultipartFile.fromPath(
      'image', // expected field name
      selectedImage!.path,
      contentType: mimeType != null ? MediaType.parse(mimeType) : null,
    );

    request.files.add(imageFile);
    request.fields.addAll(fields);

    try {
      final response = await request.send();
      return response;
    } catch (e) {
      // ignore: use_build_context_synchronously
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Upload failed: $e'), backgroundColor: Colors.red),
      );
      return null;
    }
  }
}