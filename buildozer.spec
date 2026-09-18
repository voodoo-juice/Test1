[app]

title = My App
package.name = myapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.main = main.py
requirements = python3,kivy

# Явное указание bootstrap и стабильных параметров
requirements.source.kivy = 
android.bootstrap = sdl2
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = armeabi-v7a
android.accept_sdk_license = True

orientation = portrait
version = 0.1

[buildozer]
log_level = 2
