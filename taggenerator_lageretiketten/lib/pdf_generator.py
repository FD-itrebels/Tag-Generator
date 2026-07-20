"""
Shared PDF Generation Core für Odoo + Standalone
Neue Struktur: Level/Position/Barcode/Rack (WMS-kompatibel)
"""
import csv
import io
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors


class PDFLabelGenerator:
    """Generiert farbcodierte Vektor-PDFs mit QR-Codes (410×70mm, 4 Slots)"""
    
    def __init__(self, label_width=410, label_height=70, qr_size=50):
        """
        Args:
            label_width: mm (default 410 für A4 quer minus Ränder)
            label_height: mm (default 70 für 4 Labels pro A4)
            qr_size: mm (default 50mm)
        """
        self.label_width = label_width * mm
        self.label_height = label_height * mm
        self.qr_size = qr_size * mm
        self.slot_width = self.label_width / 4  # 4 Slots nebeneinander
        
        # Padding/Margins
        self.padding_x = 2.5 * mm  # Innere Abstände
        self.padding_y = 2 * mm
        self.print_margin = 5 * mm  # 0.5cm Druckmarkierung Abstand von Rand
        
        # Farbcodierung: Slot → Farbe
        # Slot 4 (Level 1) = Gelb, Slot 3 = Orange, Slot 2 = Grün, Slot 1 (Level 4) = Blau
        self.color_map = {
            1: colors.HexColor('#ffff00'),  # Level 1 → Slot 4 (Gelb)
            2: colors.HexColor('#ffa500'),  # Level 2 → Slot 3 (Orange)
            3: colors.HexColor('#7cfc00'),  # Level 3 → Slot 2 (Grün)
            4: colors.HexColor('#00bfff'),  # Level 4 → Slot 1 (Blau)
        }
    
    def detect_delimiter(self, csv_content):
        """Erkennt CSV-Delimiter automatisch"""
        first_line = csv_content.split('\n')[0] if isinstance(csv_content, str) else csv_content.readline().decode('utf-8-sig')
        if ';' in first_line: 
            return ';'
        elif '\t' in first_line: 
            return '\t'
        else: 
            return ','
    
    def parse_csv_data(self, csv_content):
        """
        Liest CSV und gruppiert dynamisch nach (Rack, Position)
        Nur Labels mit ALLEN 4 Levels werden generiert
        
        Erwartet CSV-Spalten: Level, Position, Barcode, Rack
        """
        delimiter = self.detect_delimiter(csv_content)
        
        # Handle both file-like and string input
        if isinstance(csv_content, str):
            csv_file = io.StringIO(csv_content)
        else:
            csv_file = io.StringIO(csv_content.read().decode('utf-8-sig'))
        
        # Sammle alle Rows nach (Rack, Position)
        label_data = defaultdict(list)
        
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for row in reader:
            # Case-insensitive field matching
            level_val = None
            position_val = None
            barcode_val = None
            rack_val = None
            
            for key, val in row.items():
                if key.strip().lower() == 'level':
                    level_val = val.strip()
                elif key.strip().lower() == 'position':
                    position_val = val.strip()
                elif key.strip().lower() == 'barcode':
                    barcode_val = val.strip()
                elif key.strip().lower() == 'rack':
                    rack_val = val.strip()
            
            if not all([level_val, position_val, barcode_val, rack_val]):
                continue
            
            try:
                level_int = int(level_val)
            except ValueError:
                continue
            
            key = (rack_val, position_val)
            label_data[key].append({
                'level': level_int,
                'barcode': barcode_val,
                'rack': rack_val,
                'position': position_val
            })
        
        # Konvertiere zu Label-Liste (nur komplette Labels mit Level 1-4)
        labels = []
        for (rack, position), slots in sorted(label_data.items()):
            # Prüfe: Haben wir alle 4 Levels?
            levels_present = {slot['level'] for slot in slots}
            if levels_present == {1, 2, 3, 4}:
                # Sortiere nach Level (1, 2, 3, 4)
                slots_sorted = sorted(slots, key=lambda x: x['level'])
                labels.append({
                    'rack': rack,
                    'position': position,
                    'slots': slots_sorted  # [Level1, Level2, Level3, Level4]
                })
        
        return labels
    
    def generate_pdf(self, labels, output_buffer=None):
        """
        Generiert PDF aus Label-Liste
        
        Args:
            labels: Liste von Label-Dicts (aus parse_csv_data)
            output_buffer: BytesIO (für Odoo), None = eigenes BytesIO
            
        Returns:
            BytesIO mit PDF-Daten
        """
        if output_buffer is None:
            output_buffer = io.BytesIO()
        
        c = canvas.Canvas(output_buffer, pagesize=(self.label_width, self.label_height))
        
        for label in labels:
            rack = label['rack']
            position = label['position']
            slots = label['slots']  # [Level1, Level2, Level3, Level4]
            
            # Zeichne 4 Slots nebeneinander (Slot 4, 3, 2, 1 von links nach rechts)
            for slot_index, slot_data in enumerate(slots):
                level = slot_data['level']
                barcode = slot_data['barcode']
                x_offset = slot_index * self.slot_width
                
                # Slot-Nummer für Display (Level→Slot: 1→4, 2→3, 3→2, 4→1)
                slot_display_num = 5 - level
                
                # Farbe nach Level
                slot_color = self.color_map.get(level, colors.white)
                
                # ===== HINTERGRUND =====
                c.setFillColor(slot_color)
                c.rect(x_offset, 0, self.slot_width, self.label_height, fill=1, stroke=1)
                c.setStrokeColor(colors.black)
                c.setLineWidth(0.5)
                c.rect(x_offset, 0, self.slot_width, self.label_height, fill=0, stroke=1)
                
                # ===== RACK-KENNUNG (oben links, gedreht) =====
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 42)  # 42pt (vorher 16pt)
                c.saveState()
                c.translate(x_offset + 5*mm, self.label_height - 8*mm)
                c.rotate(90)
                c.drawCentredString(0, 0, rack)
                c.restoreState()
                
                # ===== QR-CODE (oben-links positioned, mit weißem Hintergrund) =====
                if barcode:
                    # Weiße Box hinter QR-Code
                    qr_box_padding = 1.5 * mm
                    c.setFillColor(colors.white)
                    c.setStrokeColor(colors.lightgrey)
                    c.setLineWidth(0.5)
                    qr_x_pos = x_offset + self.padding + qr_box_padding
                    qr_y_pos = self.label_height - self.qr_size - self.padding - qr_box_padding
                    c.rect(
                        qr_x_pos - qr_box_padding, 
                        qr_y_pos - qr_box_padding, 
                        self.qr_size + 2*qr_box_padding, 
                        self.qr_size + 2*qr_box_padding, 
                        fill=1, stroke=1
                    )
                    
                    # QR-Code selbst (oben-links corner positioned)
                    qr_code = qr.QrCodeWidget(barcode)
                    qr_drawing = Drawing(self.qr_size, self.qr_size)
                    qr_drawing.add(qr_code)
                    qr_drawing.drawOn(c, qr_x_pos, qr_y_pos)
                
                # ===== BARCODE-NUMMER (unten, große Schrift 24pt) =====
                c.setFont("Courier-Bold", 24)  # 24pt Mono, größer (vorher 8pt)
                c.setFillColor(colors.black)
                c.drawCentredString(x_offset + self.slot_width/2, 4*mm, str(barcode))
                
                # ===== SLOT-NUMMER (rechts oben, sehr groß 42pt) =====
                c.setFont("Helvetica-Bold", 42)  # 42pt (vorher 32pt)
                c.drawRightString(x_offset + self.slot_width - 3*mm, self.label_height - 10*mm, str(slot_display_num))
                
                # ===== LEVEL-NUMMER (rechts unten, 32pt) =====
                c.setFont("Helvetica-Bold", 32)  # 32pt (vorher 14pt)
                c.drawRightString(x_offset + self.slot_width - 3*mm, 7*mm, f"L{level}")
            
            c.showPage()
        
        c.save()
        output_buffer.seek(0)
        return output_buffer
