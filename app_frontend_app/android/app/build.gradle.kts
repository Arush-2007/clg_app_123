plugins {
    id("com.android.application")
    // START: FlutterFire Configuration
    id("com.google.gms.google-services")
    // END: FlutterFire Configuration
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin") // Flutter plugin must come last
}

android {
    namespace = "com.classified.college_app"
    compileSdk = 35 // 🔧 Use a fixed version instead of flutter.compileSdkVersion
    ndkVersion = "27.0.12077973" // 🔧 Required by Firebase

    defaultConfig {
        applicationId = "com.classified.college_app"
        minSdk = 23 // ✅ Firebase requires minSdk >= 23
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("debug") // ⚠️ Change this for production
            isMinifyEnabled = false
            isShrinkResources = false
        }
    }
}

flutter {
    source = "../.."
}
