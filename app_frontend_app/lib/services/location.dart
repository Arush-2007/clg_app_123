import 'package:geocoding/geocoding.dart';
import 'package:geolocator/geolocator.dart';

class Location {

  // Method to get location name and save it
  // Returns a string with the location name or an error message
  Future<String> getLocationAndSave() async {
    try {
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        return 'Location services are disabled';
      }

      // Check and request permissions
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          return 'Location permission denied';
        }
      }

      if (permission == LocationPermission.deniedForever) {
        return 'Location permission permanently denied';
      }

      // Get coordinates
      Position position = await Geolocator.getCurrentPosition(
        // ignore: deprecated_member_use
        desiredAccuracy: LocationAccuracy.high,
      );

      // Reverse geocode to get placemark
      List<Placemark> placemarks = await placemarkFromCoordinates(
        position.latitude,
        position.longitude,
      );

      if (placemarks.isNotEmpty) {
        final Placemark place = placemarks.first;
        final locationName = '${place.locality}, ${place.administrativeArea}';
        return locationName;
      } else {
        return 'Unknown location';
      }
    } catch (e) {
      return 'Error fetching location';
    }
  }



  // Method to get coordinates and save them
  // Returns a map with latitude and longitude or an error message
  Future<Map<String, String>> getCoordinatesAndSave() async {
    try {
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        return {'error': 'Location services are disabled'};
      }

      // Check and request permissions
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          return {'error': 'Location permission denied'};
        }
      }

      if (permission == LocationPermission.deniedForever) {
        return {'error': 'Location permission permanently denied'};
      }

      // Get coordinates
      Position position = await Geolocator.getCurrentPosition(
        // ignore: deprecated_member_use
        desiredAccuracy: LocationAccuracy.high,
      );

      return {
        'latitude': position.latitude.toString(),
        'longitude': position.longitude.toString(),
      };
    } catch (e) {
      return {'error': 'Error fetching location: $e'};
    }
  }
}
