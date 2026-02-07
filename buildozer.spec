[app]
# Datos básicos
title = Gestión Fábrica
package.name = gestionfabrica
package.domain = com.factory.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db,json,txt
source.include_patterns = factory.kv,modules/*.py,assets/*
version = 2.0.0

# REQUERIMIENTOS (Ajustados para máxima estabilidad)
# Cambiamos KivyMD a 1.1.1 y aseguramos dependencias de imagen
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, fpdf2, plyer, requests

# Pantalla
orientation = landscape
fullscreen = 0

# PERMISOS
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# CONFIGURACIÓN ANDROID (API 33 es ideal para compatibilidad actual)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

# AJUSTES DE SISTEMA
android.allow_backup = False
android.gl_backend = sdl2
warn_on_root = 1

[buildozer]
log_level = 2
