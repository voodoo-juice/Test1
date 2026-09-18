[app]

title = My App
package.name = myapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.main = main.py
requirements = python3,kivy

# Актуальные настройки и современные версии API/minapi для установки на свежие версии Android
p4a.bootstrap = sdl2
android.api = 34
android.minapi = 26
android.sdk = 34
android.ndk = 25b
android.archs = armeabi-v7a
android.accept_sdk_license = True

orientation = portrait
version = 0.1

[buildozer]
log_level = 2

# force rebuild
