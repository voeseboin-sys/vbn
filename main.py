"""
================================================================================
GESTIÓN FÁBRICA - Aplicación Android con KivyMD
Compilación vía GitHub Actions - Repositorio: voeseboin-sys/apkgithut
================================================================================

Autor: voeseboin
Email: voeseboin@gmail.com
Repositorio: https://github.com/voeseboin-sys/apkgithut

Características:
- Modo Landscape (Horizontal)
- Tema Oscuro Material Design 3
- Moneda en Guaraníes (PYG)
- Base de datos SQLite
- Generación de PDF con Share Intent nativo Android

================================================================================
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from kivy.config import Config
# Forzar modo Landscape antes de importar Window
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', '0')
Config.set('kivy', 'exit_on_escape', '0')

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemSupportingText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

# Importar módulo PDF
try:
    from modules.pdf_generator import PDFGenerator
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[WARNING] Módulo PDF no disponible")

# ==============================================================================
# BASE DE DATOS
# ==============================================================================
class DatabaseManager:
    """Gestor de base de datos SQLite para la aplicación"""
    
    def __init__(self, db_path='factory.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa todas las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de productos/inventario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                codigo TEXT UNIQUE,
                stock INTEGER DEFAULT 0,
                precio_venta REAL DEFAULT 0,
                costo_unitario REAL DEFAULT 0,
                categoria TEXT,
                fecha_creacion TEXT
            )
        ''')
        
        # Tabla de producción
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produccion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                cantidad INTEGER NOT NULL,
                fecha TEXT,
                costo_total REAL DEFAULT 0,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        # Tabla de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL,
                total REAL,
                fecha TEXT,
                cliente TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        # Tabla de gastos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concepto TEXT NOT NULL,
                monto REAL NOT NULL,
                categoria TEXT,
                fecha TEXT,
                descripcion TEXT
            )
        ''')
        
        # Tabla de balance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                tipo TEXT,
                concepto TEXT,
                monto REAL,
                saldo_acumulado REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ===== PRODUCTOS =====
    def add_producto(self, nombre, codigo, stock, precio_venta, categoria):
        conn = self.get_connection()
        cursor = conn.cursor()
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO productos (nombre, codigo, stock, precio_venta, categoria, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, codigo, stock, precio_venta, categoria, fecha))
        conn.commit()
        conn.close()
    
    def get_productos(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos ORDER BY nombre')
        productos = cursor.fetchall()
        conn.close()
        return productos
    
    def update_producto_stock(self, producto_id, cantidad):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE productos SET stock = stock + ? WHERE id = ?', (cantidad, producto_id))
        conn.commit()
        conn.close()
    
    # ===== PRODUCCIÓN =====
    def add_produccion(self, producto_id, cantidad, costo_total):
        conn = self.get_connection()
        cursor = conn.cursor()
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO produccion (producto_id, cantidad, fecha, costo_total)
            VALUES (?, ?, ?, ?)
        ''', (producto_id, cantidad, fecha, costo_total))
        cursor.execute('UPDATE productos SET stock = stock + ? WHERE id = ?', (cantidad, producto_id))
        conn.commit()
        conn.close()
    
    def get_produccion_mes(self, mes=None, anio=None):
        if mes is None:
            mes = datetime.now().month
        if anio is None:
            anio = datetime.now().year
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(cantidad), SUM(costo_total) FROM produccion 
            WHERE strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?
        ''', (f'{mes:02d}', str(anio)))
        result = cursor.fetchone()
        conn.close()
        return result if result[0] else (0, 0)
    
    # ===== VENTAS =====
    def add_venta(self, producto_id, cantidad, precio_unitario, cliente):
        conn = self.get_connection()
        cursor = conn.cursor()
        total = cantidad * precio_unitario
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO ventas (producto_id, cantidad, precio_unitario, total, fecha, cliente)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (producto_id, cantidad, precio_unitario, total, fecha, cliente))
        cursor.execute('UPDATE productos SET stock = stock - ? WHERE id = ?', (cantidad, producto_id))
        self._registrar_balance(conn, 'INGRESO', f'Venta - {cliente}', total)
        conn.commit()
        conn.close()
    
    def get_ventas(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, p.nombre, v.cantidad, v.total, v.fecha, v.cliente 
            FROM ventas v JOIN productos p ON v.producto_id = p.id
            ORDER BY v.fecha DESC LIMIT ?
        ''', (limit,))
        ventas = cursor.fetchall()
        conn.close()
        return ventas
    
    # ===== GASTOS =====
    def add_gasto(self, concepto, monto, categoria, descripcion):
        conn = self.get_connection()
        cursor = conn.cursor()
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO gastos (concepto, monto, categoria, fecha, descripcion)
            VALUES (?, ?, ?, ?, ?)
        ''', (concepto, monto, categoria, fecha, descripcion))
        self._registrar_balance(conn, 'EGRESO', concepto, monto)
        conn.commit()
        conn.close()
    
    def get_gastos_mes(self, mes=None, anio=None):
        if mes is None:
            mes = datetime.now().month
        if anio is None:
            anio = datetime.now().year
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(monto) FROM gastos 
            WHERE strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?
        ''', (f'{mes:02d}', str(anio)))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0
    
    def get_gastos(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM gastos ORDER BY fecha DESC LIMIT ?', (limit,))
        gastos = cursor.fetchall()
        conn.close()
        return gastos
    
    # ===== BALANCE =====
    def _registrar_balance(self, conn, tipo, concepto, monto):
        cursor = conn.cursor()
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('SELECT saldo_acumulado FROM balance ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        saldo_anterior = result[0] if result else 0
        
        if tipo == 'INGRESO':
            nuevo_saldo = saldo_anterior + monto
        else:
            nuevo_saldo = saldo_anterior - monto
        
        cursor.execute('''
            INSERT INTO balance (fecha, tipo, concepto, monto, saldo_acumulado)
            VALUES (?, ?, ?, ?, ?)
        ''', (fecha, tipo, concepto, monto, nuevo_saldo))
    
    def get_balance_actual(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT saldo_acumulado FROM balance ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def get_resumen_mes(self, mes=None, anio=None):
        if mes is None:
            mes = datetime.now().month
        if anio is None:
            anio = datetime.now().year
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(total) FROM ventas 
            WHERE strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?
        ''', (f'{mes:02d}', str(anio)))
        ventas_mes = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT SUM(monto) FROM gastos 
            WHERE strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?
        ''', (f'{mes:02d}', str(anio)))
        gastos_mes = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT SUM(cantidad) FROM produccion 
            WHERE strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?
        ''', (f'{mes:02d}', str(anio)))
        unidades_producidas = cursor.fetchone()[0] or 0
        
        conn.close()
        
        costo_por_unidad = gastos_mes / unidades_producidas if unidades_producidas > 0 else 0
        
        return {
            'ventas': ventas_mes,
            'gastos': gastos_mes,
            'balance': ventas_mes - gastos_mes,
            'unidades_producidas': unidades_producidas,
            'costo_por_unidad': costo_por_unidad
        }


# ==============================================================================
# FORMATO MONEDA GUARANÍES
# ==============================================================================
def format_guaranies(valor):
    """Formatea un número al estilo Guaraníes: Gs. 1.000.000"""
    if valor is None:
        valor = 0
    return f"Gs. {valor:,.0f}".replace(",", ".")


# ==============================================================================
# PANTALLAS
# ==============================================================================
class PanelScreen(MDScreen):
    """Pantalla principal del Panel de Control"""
    
    def on_enter(self):
        self.actualizar_dashboard()
    
    def actualizar_dashboard(self):
        db = MDApp.get_running_app().db
        resumen = db.get_resumen_mes()
        
        self.ids.lbl_ventas.text = format_guaranies(resumen['ventas'])
        self.ids.lbl_gastos.text = format_guaranies(resumen['gastos'])
        self.ids.lbl_balance.text = format_guaranies(resumen['balance'])
        self.ids.lbl_unidades.text = str(resumen['unidades_producidas'])
        self.ids.lbl_costo_unitario.text = format_guaranies(resumen['costo_por_unidad'])
        
        balance_total = db.get_balance_actual()
        self.ids.lbl_balance_total.text = format_guaranies(balance_total)


class InventarioScreen(MDScreen):
    """Pantalla de Gestión de Inventario"""
    
    def on_enter(self):
        self.cargar_productos()
    
    def cargar_productos(self):
        self.ids.container_productos.clear_widgets()
        db = MDApp.get_running_app().db
        productos = db.get_productos()
        
        for prod in productos:
            item = MDListItem(
                MDListItemLeadingIcon(icon="package-variant"),
                MDListItemSupportingText(
                    text=f"{prod[1]} | Stock: {prod[3]} | {format_guaranies(prod[4])}"
                ),
                on_release=lambda x, p=prod: self.ver_producto(p)
            )
            self.ids.container_productos.add_widget(item)
    
    def ver_producto(self, producto):
        self.mostrar_snackbar(f"{producto[1]} - Stock: {producto[3]}")
    
    def mostrar_snackbar(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()
    
    def abrir_dialogo_nuevo_producto(self):
        self.mostrar_snackbar("Función: Nuevo Producto")


class ProduccionScreen(MDScreen):
    """Pantalla de Registro de Producción"""
    
    def on_enter(self):
        self.cargar_productos_spinner()
    
    def cargar_productos_spinner(self):
        db = MDApp.get_running_app().db
        productos = db.get_productos()
        self.productos_list = [(p[0], p[1]) for p in productos]
    
    def registrar_produccion(self):
        try:
            cantidad = int(self.ids.txt_cantidad.text)
            costo = float(self.ids.txt_costo.text or 0)
            
            if cantidad <= 0:
                self.mostrar_error("La cantidad debe ser mayor a 0")
                return
            
            db = MDApp.get_running_app().db
            productos = db.get_productos()
            if not productos:
                self.mostrar_error("No hay productos registrados")
                return
            
            producto_id = productos[0][0]
            db.add_produccion(producto_id, cantidad, costo)
            
            self.mostrar_snackbar(f"Producción registrada: {cantidad} unidades")
            self.ids.txt_cantidad.text = ""
            self.ids.txt_costo.text = ""
            
        except ValueError:
            self.mostrar_error("Ingrese valores numéricos válidos")
    
    def mostrar_snackbar(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()
    
    def mostrar_error(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()


class VentasScreen(MDScreen):
    """Pantalla de Registro de Ventas"""
    
    def on_enter(self):
        self.cargar_ventas()
    
    def cargar_ventas(self):
        self.ids.container_ventas.clear_widgets()
        db = MDApp.get_running_app().db
        ventas = db.get_ventas(20)
        
        for v in ventas:
            item = MDListItem(
                MDListItemLeadingIcon(icon="cash-register"),
                MDListItemSupportingText(
                    text=f"{v[1]} | {v[2]} u. | {format_guaranies(v[3])} | {v[4][:10]}"
                )
            )
            self.ids.container_ventas.add_widget(item)
    
    def registrar_venta(self):
        try:
            cantidad = int(self.ids.txt_cantidad_venta.text)
            precio = float(self.ids.txt_precio_venta.text)
            cliente = self.ids.txt_cliente.text or "Cliente General"
            
            if cantidad <= 0 or precio <= 0:
                self.mostrar_error("Cantidad y precio deben ser mayores a 0")
                return
            
            db = MDApp.get_running_app().db
            productos = db.get_productos()
            if not productos:
                self.mostrar_error("No hay productos registrados")
                return
            
            producto_id = productos[0][0]
            db.add_venta(producto_id, cantidad, precio, cliente)
            
            self.mostrar_snackbar(f"Venta registrada: {format_guaranies(cantidad * precio)}")
            self.ids.txt_cantidad_venta.text = ""
            self.ids.txt_precio_venta.text = ""
            self.ids.txt_cliente.text = ""
            self.cargar_ventas()
            
        except ValueError:
            self.mostrar_error("Ingrese valores numéricos válidos")
    
    def mostrar_snackbar(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()
    
    def mostrar_error(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()


class GastosScreen(MDScreen):
    """Pantalla de Registro de Gastos"""
    
    def on_enter(self):
        self.cargar_gastos()
    
    def cargar_gastos(self):
        self.ids.container_gastos.clear_widgets()
        db = MDApp.get_running_app().db
        gastos = db.get_gastos(20)
        
        for g in gastos:
            item = MDListItem(
                MDListItemLeadingIcon(icon="cash-remove"),
                MDListItemSupportingText(
                    text=f"{g[1]} | {format_guaranies(g[2])} | {g[4][:10]}"
                )
            )
            self.ids.container_gastos.add_widget(item)
    
    def registrar_gasto(self):
        try:
            concepto = self.ids.txt_concepto_gasto.text
            monto = float(self.ids.txt_monto_gasto.text)
            categoria = self.ids.txt_categoria_gasto.text or "General"
            descripcion = self.ids.txt_descripcion_gasto.text or ""
            
            if not concepto or monto <= 0:
                self.mostrar_error("Concepto y monto son obligatorios")
                return
            
            db = MDApp.get_running_app().db
            db.add_gasto(concepto, monto, categoria, descripcion)
            
            self.mostrar_snackbar(f"Gasto registrado: {format_guaranies(monto)}")
            self.ids.txt_concepto_gasto.text = ""
            self.ids.txt_monto_gasto.text = ""
            self.ids.txt_descripcion_gasto.text = ""
            self.cargar_gastos()
            
        except ValueError:
            self.mostrar_error("Ingrese un monto válido")
    
    def mostrar_snackbar(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()
    
    def mostrar_error(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()


class ReportesScreen(MDScreen):
    """Pantalla de Generación de Reportes PDF"""
    
    def on_enter(self):
        self.actualizar_preview()
    
    def actualizar_preview(self):
        db = MDApp.get_running_app().db
        resumen = db.get_resumen_mes()
        
        preview_text = f"""
RESUMEN MENSUAL

Ventas: {format_guaranies(resumen['ventas'])}
Gastos: {format_guaranies(resumen['gastos'])}
Balance: {format_guaranies(resumen['balance'])}

Unidades Producidas: {resumen['unidades_producidas']}
Costo por Unidad: {format_guaranies(resumen['costo_por_unidad'])}

Balance Acumulado: {format_guaranies(db.get_balance_actual())}
        """
        self.ids.lbl_preview.text = preview_text
    
    def generar_pdf(self):
        """Genera PDF y abre el menú de compartir de Android"""
        if not PDF_AVAILABLE:
            self.mostrar_error("Módulo PDF no disponible")
            return
        
        try:
            db = MDApp.get_running_app().db
            pdf_gen = PDFGenerator()
            
            filepath = pdf_gen.generar_reporte_mensual(db)
            self.mostrar_snackbar(f"PDF generado")
            
            pdf_gen.compartir_pdf_android(filepath)
            
        except Exception as e:
            self.mostrar_error(f"Error: {str(e)}")
    
    def mostrar_snackbar(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()
    
    def mostrar_error(self, texto):
        MDSnackbar(
            MDSnackbarText(text=texto),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()


# ==============================================================================
# SCREEN MANAGER
# ==============================================================================
class FactoryScreenManager(ScreenManager):
    pass


# ==============================================================================
# APLICACIÓN PRINCIPAL
# ==============================================================================
class FactoryApp(MDApp):
    db = ObjectProperty(None)
    
    def build(self):
        # Configurar tema oscuro
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Teal"
        
        # Forzar landscape
        Window.rotation = 0
        
        # Inicializar base de datos
        self.db = DatabaseManager()
        
        return self.root
    
    def on_start(self):
        """Acciones al iniciar la app"""
        productos = self.db.get_productos()
        if not productos:
            self._insertar_datos_ejemplo()
    
    def _insertar_datos_ejemplo(self):
        """Inserta datos de ejemplo para pruebas"""
        self.db.add_producto("Producto A", "PROD-001", 100, 50000, "Categoría 1")
        self.db.add_producto("Producto B", "PROD-002", 50, 75000, "Categoría 1")
        self.db.add_producto("Producto C", "PROD-003", 200, 25000, "Categoría 2")


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================
if __name__ == '__main__':
    FactoryApp().run()
