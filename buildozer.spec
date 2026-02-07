[app]
title = Mi Aplicacion VBN
package.name = vbnapp
package.domain = org.voeseboin
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# REQUERIMIENTOS: Añadimos kivymd y sus dependencias de imagen
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, requests

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Configuración de Android estable
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
