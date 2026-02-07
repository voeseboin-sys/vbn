# =============================================================================
# BUILDOZER.SPEC v2.0 - Configuración corregida para GitHub Actions
# Repositorio: voeseboin-sys/vbn
#
# CORRECCIONES v2.0:
# - Requirements coinciden con requirements.txt (kivymd==1.2.0)
# - Android SDK/NDK configurados correctamente
# - Permisos de almacenamiento para PDF
# - Orientación landscape forzada
# =============================================================================

[app]

# Título de la aplicación (nombre visible)
title = Gestión Fábrica

# Nombre del paquete (minúsculas, sin espacios)
package.name = gestionfabrica

# Dominio inverso para el paquete
package.domain = com.factory.app

# Directorio fuente
source.dir = .

# Extensiones de archivos a incluir
source.include_exts = py,png,jpg,kv,atlas,ttf,db,json,txt

# Extensiones a excluir
source.exclude_exts = spec

# Directorios a excluir del build
source.exclude_dirs = tests, bin, venv, __pycache__, .git, .idea, build, dist, .github, scripts

# Patrones específicos a incluir
source.include_patterns = factory.kv,modules/*.py,assets/*

# Versión de la aplicación
version = 2.0.0

# =============================================================================
# REQUISITOS - DEBEN COINCIDIR CON requirements.txt
# =============================================================================

requirements = python3,kivy==2.2.1,kivymd==1.2.0,fpdf2,plyer,pillow

# =============================================================================
# CONFIGURACIÓN DE PANTALLA
# =============================================================================

# Orientación: landscape (horizontal) como se requiere
orientation = landscape

# Pantalla completa (0 = no, 1 = sí)
fullscreen = 0

# =============================================================================
# ICONO Y SPLASH SCREEN (opcional)
# =============================================================================

# Icono de la aplicación
# icon.filename = assets/icon.png

# Presplash (imagen mientras carga)
# presplash.filename = assets/presplash.png

# =============================================================================
# PERMISOS DE ANDROID
# =============================================================================

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# =============================================================================
# CONFIGURACIÓN ANDROID SDK/NDK
# =============================================================================

# API de Android objetivo
android.api = 34

# API mínima soportada
android.minapi = 21

# Versión del SDK de Android
android.sdk = 33

# Versión del NDK de Android
android.ndk = 25b

# Arquitecturas objetivo
android.archs = armeabi-v7a,arm64-v8a

# =============================================================================
# MODO DEBUG/RELEASE
# =============================================================================

# 1 = modo debug, 0 = modo release
android.debug = 1

# =============================================================================
# CONFIGURACIÓN DE BUILD
# =============================================================================

# Permitir backup de datos
android.allow_backup = False

# Backend de OpenGL
android.gl_backend = sdl2

# Preservar atributos para compatibilidad
android.preserve_attrs = android.support.v7.widget.FitWindowsLinearLayout

# Copiar librerías
android.copy_libs = 1

# =============================================================================
# CONFIGURACIÓN DE PLYER (Share Intent)
# =============================================================================

android.add_aars =
android.meta_data =

# =============================================================================
# OPCIONES DE BUILD (NO MODIFICAR)
# =============================================================================

buildozer.verbose = 1
build.dir = ./buildozer
bin.dir = ./bin

# =============================================================================
# NOTIFICACIONES (deshabilitadas)
# =============================================================================

android.notifications = False

# =============================================================================
# FIRMA DE RELEASE (configurar para producción)
# =============================================================================

# Para crear APK firmada en release:
# 1. Generar keystore: keytool -genkey -v -keystore my.keystore -alias myalias -keyalg RSA -keysize 2048 -validity 10000
# 2. Configurar abajo:
# android.release_artifact = apk
# android.sign = True
# android.keystore = /path/to/my.keystore
# android.keystore_password = password
# android.keyalias = myalias
# android.keyalias_password = password

# =============================================================================
# iOS (NO USADO - solo Android)
# =============================================================================

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

# =============================================================================
# CONFIGURACIÓN DE BUILDOZER
# =============================================================================

[buildozer]

# Nivel de log (0 = error, 1 = info, 2 = debug)
log_level = 2

# Advertir si se ejecuta como root
warn_on_root = 1

# Directorios de build
build_dir = ./.buildozer
bin_dir = ./bin
