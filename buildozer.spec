[app]

# Название вашего приложения
title = My App

# Имя пакета (латиницей, без пробелов)
package.name = myapp

# Домен пакета
package.domain = org.test

# Путь к исходному коду (точка означает корень репозитория)
source.dir = .

# Какие файлы включать в сборку
source.include_exts = py,png,jpg,kv,atlas

# Главный файл приложения
source.main = main.py

# Зависимости
requirements = python3,kivy

# Версии Android API и SDK, а также фиксация стабильного NDK для облака
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True

# Ориентация экрана
orientation = portrait

# Версия приложения
version = 0.1

[buildozer]

# Уровень логирования (2 — максимум подробностей для отладки)
log_level = 2
