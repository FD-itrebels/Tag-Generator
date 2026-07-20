#!/usr/bin/env python
"""Test neue PDF-Generierung - direkt ohne Odoo"""
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
    
    def __init__(self, label_width=410, label_height=70, qr_size=45):
        self.label_width = label_width * mm
        self.label_height = label_height * mm
        self.qr_size = qr_size * mm
        self.slot_width = self.label_width / 4
        
        self.color_map = {
            1: colors.HexColor('#ffff00'),  # Level 1 → Gelb
            2: colors.HexColor('#ffa500'),  # Level 2 → Orange
            3: colors.HexColor('#7cfc00'),  # Level 3 → Grün
            4: colors.HexColor('#00bfff'),  # Level 4 → Blau
        }
    
    def detect_delimiter(self, csv_content):
        first_line = csv_content.split('\n')[0]
        if ';' in first_line: return ';'
        elif '\t' in first_line: return '\t'
        else: return ','
    
    def parse_csv_data(self, csv_content):
        delimiter = self.detect_delimiter(csv_content)
        csv_file = io.StringIO(csv_content)
        
        label_data = defaultdict(list)
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        
        for row in reader:
            level_val = position_val = barcode_val = rack_val = None
            
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
        
        # Nur Labels mit allen 4 Levels
        labels = []
        for (rack, position), slots in sorted(label_data.items()):
            levels_present = {slot['level'] for slot in slots}
            if levels_present == {1, 2, 3, 4}:
                slots_sorted = sorted(slots, key=lambda x: x['level'])
                labels.append({
                    'rack': rack,
                    'position': position,
                    'slots': slots_sorted
                })
        
        return labels
    
    def generate_pdf(self, labels, output_buffer=None):
        if output_buffer is None:
            output_buffer = io.BytesIO()
        
        c = canvas.Canvas(output_buffer, pagesize=(self.label_width, self.label_height))
        
        for label in labels:
            rack = label['rack']
            position = label['position']
            slots = label['slots']
            
            for slot_index, slot_data in enumerate(slots):
                level = slot_data['level']
                barcode = slot_data['barcode']
                x_offset = slot_index * self.slot_width
                
                slot_display_num = 5 - level
                slot_color = self.color_map.get(level, colors.white)
                
                # Hintergrund
                c.setFillColor(slot_color)
                c.rect(x_offset, 0, self.slot_width, self.label_height, fill=1, stroke=1)
                c.setStrokeColor(colors.black)
                c.setLineWidth(0.5)
                c.rect(x_offset, 0, self.slot_width, self.label_height, fill=0, stroke=1)
                
                # Rack-Kennung
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 16)
                c.saveState()
                c.translate(x_offset + 8*mm, self.label_height - 10*mm)
                c.rotate(90)
                c.drawCentredString(0, 0, rack)
                c.restoreState()
                
                # QR-Code
                if barcode:
                    qr_code = qr.QrCodeWidget(barcode)
                    qr_drawing = Drawing(self.qr_size, self.qr_size)
                    qr_drawing.add(qr_code)
                    
                    qr_x = x_offset + (self.slot_width / 2) - (self.qr_size / 2)
                    qr_y = (self.label_height / 2) - (self.qr_size / 2)
                    qr_drawing.drawOn(c, qr_x, qr_y)
                
                # Barcode unten
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.black)
                c.drawCentredString(x_offset + self.slot_width/2, 3*mm, str(barcode))
                
                # Slot-Nummer
                c.setFont("Helvetica-Bold", 32)
                c.drawRightString(x_offset + self.slot_width - 3*mm, self.label_height - 15*mm, str(slot_display_num))
                
                # Level-Nummer
                c.setFont("Helvetica-Bold", 14)
                c.drawRightString(x_offset + self.slot_width - 3*mm, 6*mm, f"L{level}")
            
            c.showPage()
        
        c.save()
        output_buffer.seek(0)
        return output_buffer


# Test
generator = PDFLabelGenerator(label_width=410, label_height=70)
with open('warehouse_labels.csv', 'r', encoding='utf-8') as f:
    csv_content = f.read()

labels = generator.parse_csv_data(csv_content)
print(f'✅ {len(labels)} Labels gefunden')

# PDF Generierung
pdf_buffer = generator.generate_pdf(labels)
pdf_data = pdf_buffer.read()
print(f'✅ PDF generiert: {len(pdf_data)} bytes')

# Speichern
with open('test_warehouse_labels.pdf', 'wb') as f:
    f.write(pdf_data)
print('✅ PDF gespeichert: test_warehouse_labels.pdf')

# Erstes Label ausgeben
if labels:
    first = labels[0]
    print(f'\n📦 Erstes Label:')
    print(f'  Rack: {first["rack"]}')
    print(f'  Position: {first["position"]}')
    print(f'  Slots:')
    for slot in first['slots']:
        print(f'    Level {slot["level"]}: Barcode {slot["barcode"]}')

# Statistik
print(f'\n📊 Statistik:')
print(f'  Total Labels: {len(labels)}')
print(f'  Total Slots: {len(labels) * 4}')

# Rack-Verteilung
rack_count = defaultdict(int)
for label in labels:
    rack_count[label['rack']] += 1

for rack in sorted(rack_count.keys()):
    print(f'  {rack}: {rack_count[rack]} Labels')
