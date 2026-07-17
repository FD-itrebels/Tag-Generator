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
        title="Odoo Export Datei (CSV) auswählen",
        filetypes=[("CSV Dateien", "*.csv"), ("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
    )
    
    if not input_filepath: return

    output_pdf_path = os.path.join(os.path.dirname(os.path.abspath(input_filepath)), "Batch_Lageretiketten.pdf")

    try:
        # CSV mit gemeinsamer Core lesen
        generator = PDFLabelGenerator()
        with open(input_filepath, 'r', encoding='utf-8-sig') as f:
            csv_content = f.read()
        
        grouped_data = generator.parse_csv_data(csv_content)
        if not grouped_data:
            messagebox.showwarning("Achtung", "Keine gruppierbaren Ebenen gefunden.")
            return
        
        # PDF generieren
        with open(output_pdf_path, 'wb') as pdf_file:
            generator.generate_pdf(grouped_data, pdf_file)
        
        open_file_in_system_viewer(output_pdf_path)
        messagebox.showinfo("Erfolg", f"PDF erstellt: {output_pdf_path}")
        
    except ValueError as ve: messagebox.showerror("Datenfehler", str(ve))
    except Exception as e: messagebox.showerror("Systemfehler", f"Fehler:\n\n{str(e)}")

if __name__ == "__main__":
    main()
