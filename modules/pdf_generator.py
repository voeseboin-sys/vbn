"""
================================================================================
MÓDULO PDF GENERATOR - Gestión Fábrica
Repositorio: voeseboin-sys/apkgithut

Generación de PDF con fpdf2 + Share Intent nativo de Android
================================================================================
"""

import os
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

# Importar plyer para compartir (funciona en Android)
try:
    from plyer import share
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

# Importar Android-specific para share intent nativo
try:
    from jnius import autoclass, cast
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False


class PDFReport(FPDF):
    """Clase personalizada para generar reportes en PDF"""
    
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(15, 15, 15)
    
    def header(self):
        """Encabezado del PDF"""
        self.set_font('Arial', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, 'GESTIÓN DE FÁBRICA', 0, 1, 'C')
        
        self.set_font('Arial', '', 10)
        self.set_text_color(108, 117, 125)
        fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
        self.cell(0, 5, f'Reporte Generado: {fecha}', 0, 1, 'C')
        
        self.ln(5)
        self.set_draw_color(0, 123, 255)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(5)
    
    def footer(self):
        """Pie de página del PDF"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        """Título de sección"""
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 123, 255)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)
    
    def chapter_body(self, body):
        """Cuerpo de texto"""
        self.set_font('Arial', '', 10)
        self.set_text_color(33, 37, 41)
        self.multi_cell(0, 5, body)
        self.ln()
    
    def add_resumen_box(self, titulo, valor, color=(0, 123, 255)):
        """Agrega un cuadro de resumen"""
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        self.cell(90, 8, f'  {titulo}', 0, 0, 'L', True)
        
        self.set_fill_color(240, 240, 240)
        self.set_text_color(33, 37, 41)
        self.set_font('Arial', '', 10)
        self.cell(90, 8, f'{valor}  ', 0, 1, 'R', True)
        self.ln(3)


class PDFGenerator:
    """Generador de reportes PDF para la aplicación"""
    
    def __init__(self):
        self.output_dir = self._get_output_directory()
    
    def _get_output_directory(self):
        """Obtiene el directorio de salida para los PDFs"""
        if ANDROID_AVAILABLE:
            try:
                from android.storage import primary_external_storage_path
                base_path = primary_external_storage_path()
                pdf_dir = os.path.join(base_path, 'Documents', 'FactoryReports')
            except:
                pdf_dir = os.path.join(os.path.expanduser('~'), 'FactoryReports')
        else:
            pdf_dir = os.path.join(os.path.expanduser('~'), 'FactoryReports')
        
        os.makedirs(pdf_dir, exist_ok=True)
        return pdf_dir
    
    def format_guaranies(self, valor):
        """Formatea número a formato Guaraníes"""
        if valor is None:
            valor = 0
        return f"Gs. {valor:,.0f}".replace(",", ".")
    
    def generar_reporte_mensual(self, db, mes=None, anio=None):
        """
        Genera un reporte mensual en PDF
        
        Args:
            db: Instancia de DatabaseManager
            mes: Mes del reporte (default: mes actual)
            anio: Año del reporte (default: año actual)
        
        Returns:
            str: Ruta del archivo PDF generado
        """
        if mes is None:
            mes = datetime.now().month
        if anio is None:
            anio = datetime.now().year
        
        resumen = db.get_resumen_mes(mes, anio)
        balance_total = db.get_balance_actual()
        
        pdf = PDFReport()
        pdf.add_page()
        
        nombre_mes = self._get_nombre_mes(mes)
        pdf.chapter_title(f'RESUMEN MENSUAL - {nombre_mes} {anio}')
        
        pdf.chapter_title('📊 RESUMEN FINANCIERO')
        pdf.add_resumen_box('TOTAL DE VENTAS', self.format_guaranies(resumen['ventas']), (40, 167, 69))
        pdf.add_resumen_box('TOTAL DE GASTOS', self.format_guaranies(resumen['gastos']), (220, 53, 69))
        
        balance_color = (40, 167, 69) if resumen['balance'] >= 0 else (220, 53, 69)
        pdf.add_resumen_box('BALANCE DEL MES', self.format_guaranies(resumen['balance']), balance_color)
        
        pdf.ln(5)
        
        pdf.chapter_title('🏭 RESUMEN DE PRODUCCIÓN')
        pdf.add_resumen_box('UNIDADES PRODUCIDAS', f"{resumen['unidades_producidas']} unidades", (0, 123, 255))
        pdf.add_resumen_box('COSTO POR UNIDAD', self.format_guaranies(resumen['costo_por_unidad']), (255, 193, 7))
        
        pdf.ln(5)
        
        pdf.chapter_title('💰 BALANCE ACUMULADO')
        pdf.add_resumen_box('SALDO TOTAL', self.format_guaranies(balance_total), (111, 66, 193))
        
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 5, '* Los cálculos de costo por unidad incluyen todos los gastos de fábrica del mes.', 0, 1, 'L')
        pdf.cell(0, 5, '* El balance acumulado representa el saldo histórico de ingresos menos gastos.', 0, 1, 'L')
        
        filename = f"Reporte_Fabrica_{anio}_{mes:02d}_{datetime.now().strftime('%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        
        return filepath
    
    def compartir_pdf_android(self, filepath):
        """
        Abre el menú de compartir de Android para el PDF generado
        Usa el Share Intent nativo de Android
        """
        if not ANDROID_AVAILABLE:
            print(f"[DEBUG] No estamos en Android. Archivo: {filepath}")
            if PLYER_AVAILABLE:
                try:
                    share.file(filepath, title='Compartir Reporte', text='Reporte de Gestión de Fábrica', 
                              app='application/pdf')
                except Exception as e:
                    print(f"[DEBUG] Plyer share error: {e}")
            return
        
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            Context = autoclass('android.content.Context')
            
            activity = PythonActivity.mActivity
            file = File(filepath)
            
            try:
                FileProvider = autoclass('androidx.core.content.FileProvider')
                package_name = activity.getPackageName()
                uri = FileProvider.getUriForFile(
                    activity,
                    f"{package_name}.fileprovider",
                    file
                )
            except:
                uri = Uri.fromFile(file)
            
            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.setType('application/pdf')
            intent.putExtra(Intent.EXTRA_STREAM, uri)
            intent.putExtra(Intent.EXTRA_SUBJECT, 'Reporte de Gestión de Fábrica')
            intent.putExtra(Intent.EXTRA_TEXT, 'Adjunto el reporte de gestión de fábrica.')
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            
            chooser = Intent.createChooser(intent, 'Compartir Reporte PDF')
            activity.startActivity(chooser)
            
        except Exception as e:
            print(f"[ERROR] Error al compartir PDF: {e}")
            if PLYER_AVAILABLE:
                try:
                    share.file(filepath, title='Compartir Reporte')
                except:
                    pass
    
    def _get_nombre_mes(self, mes):
        """Devuelve el nombre del mes en español"""
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return meses.get(mes, 'Mes desconocido')


def generar_y_compartir_pdf(db):
    """Genera PDF y lo comparte (función de conveniencia)"""
    generator = PDFGenerator()
    filepath = generator.generar_reporte_mensual(db)
    generator.compartir_pdf_android(filepath)
    return filepath
