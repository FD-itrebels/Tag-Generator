

Dieses Dokument ist so geschrieben, dass du es als "Context" oder "Prompt" direkt in GitHub Copilot, Cursor oder dein lokales Setup werfen kannst. Der Agent weiß dann sofort, was das Ziel ist, welche Hürden wir bereits umschifft haben und welchen Code er aufsetzen muss.


Projektdokumentation: Odoo Batch-Etikettengenerator (Lokal)1. Projektkontext & ZielsetzungDieses Projekt dient der Erstellung von hochauflösenden, farbcodierten Vektor-PDF-Etiketten für ein Logistiklager.Die Herausforderung: Das führende System ist Odoo SaaS. Odoo kann standardmäßig keine 4-in-1 Sammel-Etiketten drucken (Gruppierung mehrerer Fächer auf einem Ausdruck). Seriendrucke über Microsoft Word sind bei großen Datenmengen (Batch-Verarbeitung) wegen Speichermangel abgestürzt.Die Lösung: Eine Entkopplung von Daten und Layout. Odoo wird lediglich für einen simplen CSV/Excel-Export der Lagerorte genutzt. Ein isoliertes, lokales Python-Skript liest diese CSV, gruppiert die Daten logisch und rendert via ReportLab ressourcenschonend ein Batch-PDF, welches sich sofort im lokalen Standard-Viewer öffnet.2. Systemvoraussetzungen (Tech Stack)Python 3.x (Lokal auf dem Windows/Mac-Rechner des Lagermitarbeiters)Bibliothek: reportlab (Zuständig für das PDF-Rendering via Canvas-Ansatz)Integrierte Bibliotheken: csv, os, platform, tkinter (für den simplen Dateiauswahl-Dialog)3. Datenstruktur (Input)Das System erwartet einen Export aus Odoo im CSV-Format (Trennzeichen automatisch erkannt: ;, , oder \t).Die zwingend erforderlichen Spaltenköpfe (inklusive Fallbacks) sind: Regal, Ebene, Fach, Barcode.Beispielhafter Test-Datensatz (odoo_export_test.csv):Regal;Ebene;Fach;Barcode
R - 109;34;4;1109434
R - 109;34;3;1109334
R - 109;34;2;1109234
R - 109;34;1;1109134
R - 108;12;4;1108124
R - 108;12;3;1108123
R - 108;12;2;1108122
R - 108;12;1;1108121
4. Applikationslogik (Der Code)Der folgende Code beinhaltet die vollständige Logik zur Fehlerabfangung (BOM-Handling, Delimiter-Erkennung), zur Gruppierung der Fächer und zum geometrischen Rendering der Farbboxen und QR-Codes.Datei: etikettendruck.pyimport csv
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
                qr_code.barWidth = 30 * mm
                qr_code.barHeight = 30 * mm
                qr_drawing = Drawing(30*mm, 30*mm)
                qr_drawing.add(qr_code)
                
                qr_x = x_offset + (box_width / 2) - (15 * mm)
                qr_y = (label_height / 2) - (15 * mm)
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
5. Anweisungen für den initialisierenden AI-AgentenLege eine virtuelle Umgebung (venv) für das Projekt an.Erstelle eine requirements.txt mit dem Eintrag reportlab.Installiere die Abhängigkeiten.Lege die Datei odoo_export_test.csv mit den Testdaten an.Führe etikettendruck.py aus, wähle die Test-CSV und verifiziere, dass das PDF generiert und geöffnet wird.