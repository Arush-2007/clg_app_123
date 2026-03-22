import 'dart:convert';

import 'package:http/http.dart' as http;

class DatabaseMethods{

  //creating user
  Future<String> createUser({
  required String email,
  required String password,
}) async {
  String res = 'user-created';
  final url = Uri.parse('https://89c2-103-170-69-228.ngrok-free.app/users/');

  final response = await http.post(
    url,
    headers: {
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'email': email,
      'password': password,
    }),
  );

  if (response.statusCode == 200) {
    return res;
  } else {
    res = response.body;
    return res;
  }
}


}