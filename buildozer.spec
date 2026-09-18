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

# Зависимости (для базового Kivy-приложения)
requirements = python3,kivy

# Ориентация экрана
orientation = portrait

# Версия приложения
version = 0.1

[buildozer]

# Уровень логирования (2 — максимум подробностей для отладки)
log_level = 2
