import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

const Color fireColor = Color(0xFFFF5722);
const Color fireAccent = Color(0xFFFFD54F); // warm amber
const Color fireBackgroundLight = Color(0xFFFFF3E0); // soft orange-white
const Color fireBackgroundDark = Color(0xFF1C1C1C); // deep dark gray

final ThemeData lightMode = ThemeData(
  brightness: Brightness.light,
  scaffoldBackgroundColor: fireBackgroundLight,
  primaryColor: fireColor,
  colorScheme: const ColorScheme.light(
    primary: fireColor,
    secondary: fireAccent,
    surface: Colors.white,
    onPrimary: Colors.white,
    onSecondary: Colors.black87,
    onSurface: Colors.black87,
    onError: Colors.white,
    error: Colors.redAccent,
  ),
  textTheme: GoogleFonts.poppinsTextTheme().apply(
    bodyColor: Colors.black87,
    displayColor: Colors.black87,
  ),
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: Colors.white,
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: fireColor, width: 1.5),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: fireAccent, width: 2),
    ),
    prefixIconColor: fireColor,
  ),
  appBarTheme: AppBarTheme(
    backgroundColor: fireColor,
    titleTextStyle: GoogleFonts.poppins(
      color: Colors.white,
      fontWeight: FontWeight.bold,
      fontSize: 20,
    ),
    iconTheme: const IconThemeData(color: Colors.white),
  ),
);



final ThemeData darkMode = ThemeData(
  brightness: Brightness.dark,
  scaffoldBackgroundColor: fireBackgroundDark,
  primaryColor: fireColor,
  colorScheme: const ColorScheme.dark(
    primary: fireColor,
    secondary: fireAccent,
    surface: Color(0xFF2C2C2C),
    onPrimary: Colors.black,
    onSecondary: Colors.black,
    onSurface: Colors.white,
    onError: Colors.black,
    error: Colors.redAccent,
  ),
  textTheme: GoogleFonts.poppinsTextTheme().apply(
    bodyColor: Colors.white,
    displayColor: Colors.white,
  ),
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: const Color(0xFF2C2C2C),
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: fireAccent, width: 1.5),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: fireColor, width: 2),
    ),
    prefixIconColor: fireAccent,
  ),
  appBarTheme: AppBarTheme(
    backgroundColor: fireColor,
    titleTextStyle: GoogleFonts.poppins(
      color: Colors.white,
      fontWeight: FontWeight.bold,
      fontSize: 20,
    ),
    iconTheme: const IconThemeData(color: Colors.white),
  ),
);
