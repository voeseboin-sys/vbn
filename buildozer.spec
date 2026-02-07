[app]
title = Gestión Fábrica
package.name = gestionfabrica
package.domain = com.factory.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db,json,txt
# IMPORTANTE: Incluimos la carpeta modules donde está tu PDFGenerator
source.include_patterns = factory.kv,modules/*.py,assets/*
version = 2.0.0

# REQUERIMIENTOS: Actualizados para KivyMD 2.0.1 (Material 3)
requirements = python3, kivy==2.3.0, https://github.com/kivymd/KivyMD/archive/master.zip, pillow, fpdf2, plyer, requests, materialyoucolor

orientation = landscape
fullscreen = 0

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
