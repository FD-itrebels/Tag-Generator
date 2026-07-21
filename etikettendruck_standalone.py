"""
Standalone Etikettendruck für Warehouse Labels
Funktioniert OHNE Odoo - nur Python + reportlab
CSV Format: Level, Position, Barcode, Rack
"""
import os
import sys
import platform
import tkinter as tk
from tkinter import filedialog, messagebox
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
        self.label_width = label_width * mm
        self.label_height = label_height * mm
        self.qr_size = qr_size * mm
        self.slot_width = self.label_width / 4
        
        # Padding/Margins
        self.padding_x = 2.5 * mm  # Innere Abstände
        self.padding_y = 2 * mm
        self.print_margin = 5 * mm  # 0.5cm Druckmarkierung Abstand von Rand
        
        self.color_map = {
            1: colors.HexColor('#ffff00'),  # Level 1 → Gelb
            2: colors.HexColor('#ffa500'),  # Level 2 → Orange
            3: colors.HexColor('#7cfc00'),  # Level 3 → Grün
            4: colors.HexColor('#00bfff'),  # Level 4 → Blau
        }
    
    def detect_delimiter(self, csv_content):
        """Erkennt CSV-Delimiter automatisch"""
        first_line = csv_content.split('\n')[0]
        if ';' in first_line: return ';'
        elif '\t' in first_line: return '\t'
        else: return ','
    
    def parse_csv_data(self, csv_content):
        """
        Liest CSV und gruppiert dynamisch nach (Rack, Position)
        Nur Labels mit ALLEN 4 Levels werden generiert
        """
        delimiter = self.detect_delimiter(csv_content)
        csv_file = io.StringIO(csv_content)
        
        label_data = defaultdict(list)
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        
        for row in reader:
            # Case-insensitive field matching
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
                slots_sorted = sorted(slots, key=lambda x: x['level'], reverse=True)
                labels.append({
                    'rack': rack,
                    'position': position,
                    'slots': slots_sorted
                })
        
        return labels
    
    def generate_pdf(self, labels, output_buffer=None):
        """Generiert PDF aus Label-Liste mit Magenta Druckmarkierung"""
        if output_buffer is None:
            output_buffer = io.BytesIO()
        
        c = canvas.Canvas(output_buffer, pagesize=(self.label_width, self.label_height))
        
        for label in labels:
            rack = label['rack']
            position = label['position']
            slots = label['slots']
            
            # Zeichne 4 Slots nebeneinander
            for slot_index, slot_data in enumerate(slots):
                level = slot_data['level']
                barcode = slot_data['barcode']
                x_offset = slot_index * self.slot_width
                
                slot_display_num = level
                slot_color = self.color_map.get(level, colors.white)
                
                # ===== HINTERGRUND =====
                c.setFillColor(slot_color)
                c.rect(x_offset, 0, self.slot_width, self.label_height, fill=1, stroke=1)
                c.setStrokeColor(colors.black)
                c.setLineWidth(0.5)
                c.rect(x_offset, 0, self.slot_width, self.label_height, fill=0, stroke=1)
                
                # ===== RACK-KENNUNG (links, vertikal gedreht) =====
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 31)
                # Nur für den blauen Slot (slot_index 0) weiter nach innen verschieben
                rack_offset = 20*mm if slot_index == 0 else 18*mm
                c.saveState()
                c.translate(x_offset + rack_offset, 20*mm)
                c.rotate(90)
                c.drawString(0, 0, rack)
                c.restoreState()
                
                # ===== QR-CODE (oben-mitte mit weißem Hintergrund) =====
                if barcode:
                    # Gemeinsamer Center für Box + QR
                    qr_box_size = 42 * mm
                    qr_size = 32 * mm
                    slot_center_x = x_offset + self.slot_width / 2
                    slot_center_y = self.label_height - 10*mm - qr_box_size / 2
                    
                    # Weiße Box - unabhängig vom QR
                    c.setFillColor(colors.white)
                    c.setStrokeColor(colors.lightgrey)
                    c.setLineWidth(0.5)
                    qr_box_x = slot_center_x - qr_box_size / 2
                    qr_box_y = slot_center_y - qr_box_size / 2
                    c.rect(
                        qr_box_x,
                        qr_box_y,
                        qr_box_size,
                        qr_box_size,
                        fill=1, stroke=1
                    )
                    
                    # QR-Code - unabhängig von Box, gleicher Center
                    qr_code = qr.QrCodeWidget(barcode, barBorder=1)
                    qr_drawing = Drawing(qr_size, qr_size)
                    qr_drawing.add(qr_code)
                    qr_x = slot_center_x - qr_size / 2
                    qr_y = slot_center_y - qr_size / 2
                    qr_drawing.drawOn(c, qr_x, qr_y)
                
                # ===== BARCODE-NUMMER (unten center) =====
                c.setFillColor(colors.black)
                c.setFont("Helvetica", 22)
                c.drawCentredString(x_offset + self.slot_width/2, 7*mm, str(barcode))
                
                # ===== SLOT-NUMMER/LEVEL (oben rechts, 42pt) =====
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 64)
                c.drawRightString(x_offset + self.slot_width - 11*mm, self.label_height - 28*mm, str(slot_display_num))
                
                # ===== POSITION-ZIFFER (unten rechts) =====
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 42)
                c.drawRightString(x_offset + self.slot_width - 9*mm, 20*mm, position)
            
            # ===== DRUCK-MARKIERUNG (Magenta Border 5mm von Rand) - NACH allen Slots =====
            c.setStrokeColor(colors.HexColor('#ff00ff'))  # Magenta
            c.setLineWidth(1.5)  # Dickere Linie für bessere Sichtbarkeit
            margin = 5 * mm  # 5mm von Rand
            c.rect(
                margin, margin,
                self.label_width - 2*margin,
                self.label_height - 2*margin,
                fill=0, stroke=1
            )
            
            c.showPage()
        
        c.save()
        output_buffer.seek(0)
        return output_buffer


def open_file_in_system_viewer(filepath):
    """Öffnet das PDF im Standard-Viewer des OS"""
    system_os = platform.system()
    if system_os == 'Darwin': 
        os.system(f'open "{filepath}"')
    elif system_os == 'Windows': 
        os.startfile(filepath)
    else: 
        os.system(f'xdg-open "{filepath}"')


def main():
    """Steuert den GUI-Dialog und den Ablauf"""
    root = tk.Tk()
    root.withdraw()
    
    input_filepath = filedialog.askopenfilename(
        title="Warehouse Labels CSV auswählen",
        filetypes=[("CSV Dateien", "*.csv"), ("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
    )
    
    if not input_filepath:
        return

    output_pdf_path = os.path.join(
        os.path.dirname(os.path.abspath(input_filepath)), 
        "Warehouse_Labels.pdf"
    )

    try:
        # CSV lesen
        with open(input_filepath, 'r', encoding='utf-8-sig') as f:
            csv_content = f.read()
        
        # PDF generieren
        generator = PDFLabelGenerator(label_width=410, label_height=70, qr_size=90)
        labels = generator.parse_csv_data(csv_content)
        
        if not labels:
            messagebox.showwarning("Achtung", "Keine vollständigen Labels gefunden.\n\nBenötigt: Level 1-4 pro (Rack, Position) Paar")
            return
        
        pdf_buffer = generator.generate_pdf(labels)
        
        # Zu Datei schreiben
        with open(output_pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_buffer.read())
        
        # Öffnen
        open_file_in_system_viewer(output_pdf_path)
        
        messagebox.showinfo("✅ Erfolg", f"PDF erstellt!\n\n📊 {len(labels)} Labels\n📄 {len(labels) * 4} Slots\n\n📍 {output_pdf_path}")
        
    except ValueError as ve:
        messagebox.showerror("Datenfehler", str(ve))
    except Exception as e:
        messagebox.showerror("Systemfehler", f"Fehler:\n\n{str(e)}")
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
