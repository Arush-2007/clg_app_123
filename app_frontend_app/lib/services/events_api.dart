import 'dart:convert';

import 'package:college_app/config/api_config.dart';
import 'package:http/http.dart' as http;

class EventsApi {
  Future<List<Map<String, String>>> fetchEvents({required String status}) async {
    final response = await http
        .get(ApiConfig.endpoint('/events?status=$status'))
        .timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      return [];
    }

    final decoded = jsonDecode(response.body);
    if (decoded is! List) return [];

    return decoded
        .map<Map<String, String>>((e) => {
              'title': (e['title'] ?? 'Untitled').toString(),
              'imageURL': (e['image_url'] ?? 'assets/images/testing/xyz.gif').toString(),
            })
        .toList();
  }
}
