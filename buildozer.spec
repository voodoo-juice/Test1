[app]

title = My App
package.name = myapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.main = main.py
requirements = python3,kivy

# Исправленные параметры для SDK и лицензий
android.api = 33
android.minapi = 21
android.sdk = 33
android.accept_sdk_license = True

orientation = portrait
version = 0.1

[buildozer]
log_level = 2
