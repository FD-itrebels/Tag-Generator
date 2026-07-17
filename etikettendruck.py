import csv
import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors

def detect_delimiter(filepath):
    """Prüft das erste Zeichenfolgen-Muster, um das korrekte Trennzeichen zu identifizieren."""
    with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
        first_line = csvfile.readline()
        if ';' in first_line: return ';'
        elif '\t' in first_line: return '\t'
        else: return ','

def process_csv_data(filepath):
    """Liest rohe Exportdaten ein und strukturiert sie hierarchisch nach Regal und Ebene um."""
    groups = {}
    delimiter = detect_delimiter(filepath)
    
    with open(filepath, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        
        headers = reader.fieldnames
        if not headers:
            raise ValueError("Die Datei ist leer oder enthält keine verwertbaren Spaltenköpfe.")
            
        for row_number, row in enumerate(reader, start=2):
            shelf = str(row.get('Regal', row.get('shelf', ''))).strip()
            level = str(row.get('Ebene', row.get('level', ''))).strip()
            slot = str(row.get('Fach', row.get('slot', ''))).strip()
            barcode_id = str(row.get('Barcode', row.get('barcode', ''))).strip()
            
            if not shelf or not level: continue
                
            group_key = f"{shelf}_{level}"
            if group_key not in groups:
                groups[group_key] = {'shelf': shelf, 'level': level, 'slots': {}}
            groups[group_key]['slots'][slot] = barcode_id
            
    return groups

def generate_pdf_labels(grouped_data, output_filename):
    """Nutzt ReportLab, um die gruppierten Daten in ein mehrfarbiges Vektor-PDF zu zeichnen."""
    label_width = 400 * mm
    label_height = 60 * mm
    
    c = canvas.Canvas(output_filename, pagesize=(label_width, label_height))
    box_width = label_width / 4
    
    color_map = {
        '4': colors.HexColor('#ffff00'), # Gelb
        '3': colors.HexColor('#ffa500'), # Orange
        '2': colors.HexColor('#7cfc00'), # Grün
        '1': colors.HexColor('#00bfff')  # Blau
    }

    for key, group in grouped_data.items():
        shelf = group['shelf']
        level = group['level']
        
        for i, slot_num in enumerate(['4', '3', '2', '1']):
            x_offset = i * box_width
            slot_color = color_map.get(slot_num, colors.white)
            barcode_data = group['slots'].get(slot_num, "FEHLER!")
            
            # Hintergrund
            c.setFillColor(slot_color)
            c.rect(x_offset, 0, box_width, label_height, fill=1, stroke=1)
            
            # Regal (gedreht)
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 24)
            c.saveState()
            c.translate(x_offset + 15*mm, label_height / 2)
            c.rotate(90)
            c.drawCentredString(0, 0, shelf)
            c.restoreState()
            
            # QR Code
            if barcode_data != "FEHLER!":
                qr_code = qr.QrCodeWidget(barcode_data)
                qr_code.barWidth = 45 * mm
                qr_code.barHeight = 45 * mm
                qr_drawing = Drawing(45*mm, 45*mm)
                qr_drawing.add(qr_code)
                
                qr_x = x_offset + (box_width / 2) - (22.5 * mm)
                qr_y = (label_height / 2) - (22.5 * mm)
                qr_drawing.drawOn(c, qr_x, qr_y)
            
            # Text unten
            c.setFont("Helvetica", 12)
            c.drawCentredString(x_offset + (box_width / 2), 5*mm, str(barcode_data))
            
            # Nomenklatur rechtsbündig
            c.setFont("Helvetica-Bold", 72)
            c.drawRightString(x_offset + box_width - 5*mm, label_height - 25*mm, slot_num)
            c.setFont("Helvetica-Bold", 36)
            c.drawRightString(x_offset + box_width - 5*mm, 5*mm, level)
            
        c.showPage()
    c.save()

def open_file_in_system_viewer(filepath):
    """Öffnet das PDF im Standard-Viewer des OS."""
    system_os = platform.system()
    if system_os == 'Darwin': os.system(f'open "{filepath}"')
    elif system_os == 'Windows': os.startfile(filepath)
    else: os.system(f'xdg-open "{filepath}"')

def main():
    """Steuert den GUI-Dialog und den Ablauf."""
    root = tk.Tk()
    root.withdraw()
    
    input_filepath = filedialog.askopenfilename(
        title="Odoo Export Datei (CSV) auswählen",
        filetypes=[("CSV Dateien", "*.csv"), ("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
    )
    
    if not input_filepath: return

    output_pdf_path = os.path.join(os.path.dirname(os.path.abspath(input_filepath)), "Batch_Lageretiketten.pdf")

    try:
        grouped_data = process_csv_data(input_filepath)
        if not grouped_data:
            messagebox.showwarning("Achtung", "Keine gruppierbaren Ebenen gefunden.")
            return
        generate_pdf_labels(grouped_data, output_pdf_path)
        open_file_in_system_viewer(output_pdf_path)
        
    except ValueError as ve: messagebox.showerror("Datenfehler", str(ve))
    except Exception as e: messagebox.showerror("Systemfehler", f"Fehler:\n\n{str(e)}")

if __name__ == "__main__":
    main()
