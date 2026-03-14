# Flutter — keep only required framework classes
-keep class io.flutter.app.FlutterApplication { *; }
-keep class io.flutter.app.FlutterActivity { *; }
-keep class io.flutter.plugin.editing.** { *; }
-keep class io.flutter.embedding.** { *; }
-keep class io.flutter.plugins.** { *; }

# Google Mobile Ads
-keep class com.google.android.gms.ads.** { *; }
-keep class com.google.ads.** { *; }

# Keep native ad factories
-keep class com.yakmeogeo.app.ListTileNativeAdFactory { *; }

# Google Play Core (referenced by Flutter engine for deferred components)
-dontwarn com.google.android.play.core.splitcompat.**
-dontwarn com.google.android.play.core.splitinstall.**
-dontwarn com.google.android.play.core.tasks.**
