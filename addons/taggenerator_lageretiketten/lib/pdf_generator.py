"""
Shared PDF Generation Core für Odoo + Standalone
"""
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors


class PDFLabelGenerator:
    """Generiert farbcodierte Vektor-PDFs mit QR-Codes"""
    
    def __init__(self, label_width=400, label_height=60, qr_size=45):
        self.label_width = label_width * mm
        self.label_height = label_height * mm
        self.qr_size = qr_size * mm
        self.color_map = {
            '4': colors.HexColor('#ffff00'),  # Gelb
            '3': colors.HexColor('#ffa500'),  # Orange
            '2': colors.HexColor('#7cfc00'),  # Grün
            '1': colors.HexColor('#00bfff'),  # Blau
        }
    
    def detect_delimiter(self, csv_content):
        """Erkennt Delimiter automatisch"""
        first_line = csv_content.split('\n')[0] if isinstance(csv_content, str) else csv_content.readline().decode('utf-8-sig')
        if ';' in first_line: return ';'
        elif '\t' in first_line: return '\t'
        else: return ','
    
    def parse_csv_data(self, csv_content):
        """Liest CSV und gruppiert hierarchisch nach Regal/Ebene"""
        groups = {}
        delimiter = self.detect_delimiter(csv_content)
        
        # Handle both file-like and string input
        if isinstance(csv_content, str):
            csv_file = io.StringIO(csv_content)
        else:
            csv_file = io.StringIO(csv_content.read().decode('utf-8-sig'))
        
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        
        for row in reader:
            shelf = str(row.get('Regal', row.get('shelf', ''))).strip()
            level = str(row.get('Ebene', row.get('level', ''))).strip()
            slot = str(row.get('Fach', row.get('slot', ''))).strip()
            barcode_id = str(row.get('Barcode', row.get('barcode', ''))).strip()
            
            if not shelf or not level:
                continue
            
            group_key = f"{shelf}_{level}"
            if group_key not in groups:
                groups[group_key] = {'shelf': shelf, 'level': level, 'slots': {}}
            groups[group_key]['slots'][slot] = barcode_id
        
        return groups
    
    def generate_pdf(self, grouped_data, output_buffer=None):
        """Generiert PDF aus gruppierter Datenstruktur
        
        Args:
            grouped_data: Dict mit Regal/Ebene-Gruppen
            output_buffer: BytesIO-Objekt (für Odoo), None = Datei
            
        Returns:
            BytesIO oder None (je nach output_buffer)
        """
        if output_buffer is None:
            output_buffer = io.BytesIO()
        
        c = canvas.Canvas(output_buffer, pagesize=(self.label_width, self.label_height))
        box_width = self.label_width / 4
        
        for group in grouped_data.values():
            shelf = group['shelf']
            level = group['level']
            
            for i, slot_num in enumerate(['4', '3', '2', '1']):
                x_offset = i * box_width
                slot_color = self.color_map.get(slot_num, colors.white)
                barcode_data = group['slots'].get(slot_num, "FEHLER!")
                
                # Hintergrund
                c.setFillColor(slot_color)
                c.rect(x_offset, 0, box_width, self.label_height, fill=1, stroke=1)
                
                # Regal (gedreht)
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 24)
                c.saveState()
                c.translate(x_offset + 15*mm, self.label_height / 2)
                c.rotate(90)
                c.drawCentredString(0, 0, shelf)
                c.restoreState()
                
                # QR Code
                if barcode_data != "FEHLER!":
                    qr_code = qr.QrCodeWidget(barcode_data)
                    qr_drawing = Drawing(self.qr_size, self.qr_size)
                    qr_drawing.add(qr_code)
                    
                    qr_x = x_offset + (box_width / 2) - (self.qr_size / 2)
                    qr_y = (self.label_height / 2) - (self.qr_size / 2)
                    qr_drawing.drawOn(c, qr_x, qr_y)
                
                # Text unten
                c.setFont("Helvetica", 12)
                c.drawCentredString(x_offset + (box_width / 2), 5*mm, str(barcode_data))
                
                # Nomenklatur
                c.setFont("Helvetica-Bold", 72)
                c.drawRightString(x_offset + box_width - 5*mm, self.label_height - 25*mm, slot_num)
                c.setFont("Helvetica-Bold", 36)
                c.drawRightString(x_offset + box_width - 5*mm, 5*mm, level)
            
            c.showPage()
        
        c.save()
        output_buffer.seek(0)
        return output_buffer
