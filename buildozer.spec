[app]
title = Mi Aplicacion VBN
package.name = vbnapp
package.domain = org.voeseboin
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# (IMPORTANTE) Versiones para evitar error de AIDL
android.api = 34
android.minapi = 21
android.build_tools_version = 34.0.0
android.ndk = 25b
android.accept_sdk_license = True

# (Opcional) Si tu app usa permisos, añadelos aquí:
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
