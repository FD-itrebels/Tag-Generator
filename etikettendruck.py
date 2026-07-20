import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox
from taggenerator_lageretiketten.lib import PDFLabelGenerator

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
        title="Warehouse Labels CSV auswählen",
        filetypes=[("CSV Dateien", "*.csv"), ("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
    )
    
    if not input_filepath: return

    output_pdf_path = os.path.join(os.path.dirname(os.path.abspath(input_filepath)), "Warehouse_Labels.pdf")

    try:
        # CSV mit gemeinsamer Core lesen und verarbeiten
        generator = PDFLabelGenerator(label_width=410, label_height=70)
        with open(input_filepath, 'r', encoding='utf-8-sig') as f:
            csv_content = f.read()
        
        # Neue Struktur: parse_csv_data gibt Label-Liste zurück
        labels = generator.parse_csv_data(csv_content)
        if not labels:
            messagebox.showwarning("Achtung", "Keine vollständigen Labels gefunden (benötigt Level 1-4 pro Position).")
            return
        
        # PDF generieren (gibt BytesIO zurück)
        pdf_buffer = generator.generate_pdf(labels)
        
        # Zu Datei schreiben
        with open(output_pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_buffer.read())
        
        open_file_in_system_viewer(output_pdf_path)
        messagebox.showinfo("Erfolg", f"✅ PDF erstellt: {len(labels)} Labels\n\n{output_pdf_path}")
        
    except ValueError as ve: messagebox.showerror("Datenfehler", str(ve))
    except Exception as e: messagebox.showerror("Systemfehler", f"Fehler:\n\n{str(e)}")

if __name__ == "__main__":
    main()

