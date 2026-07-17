# Tag Generator – Batch-Etikettendruck

Entkoppelte Lösung für farbcodierte Lageretiketten aus Odoo SaaS (+ Standalone-Script).

## 📁 Projektstruktur

```
taggenerator/
├── etikettendruck.py              # Standalone Python-Script
├── requirements.txt               # Dependencies (reportlab)
├── odoo_export_test.csv           # Test-Daten
│
├── taggenerator_lageretiketten/    # 🆕 Odoo 19 Custom Module
│   ├── __manifest__.py            # Modul-Metadaten
│   ├── models/label_batch.py       # Datenmodell
│   ├── controllers/main.py         # Web-API (zukünftig)
│   ├── views/                      # UI (Forms, Lists)
│   ├── lib/pdf_generator.py        # Shared PDF-Core (DRY)
│   └── README.md                   # Modul-Doku
│
└── README.md                       # Dieses File
```

## 🚀 Use Cases

### Option A: Standalone (Lokal)
```bash
python etikettendruck.py
→ GUI-Dialog → CSV auswählen → PDF generiert + geöffnet
```

### Option B: Odoo Integration
```
Odoo UI → Lageretiketten → CSV hochladen → PDF generieren → Download
```

## 🔧 Tech Stack

- **Python 3.12+**
- **ReportLab** – Vektor-PDF-Rendering
- **Odoo 19** – Custom Module (optional)
- **Git** – Versionskontrolle

## 📋 Installation

### Standalone

```bash
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\python etikettendruck.py
```

### Odoo Module (odoo.sh)

Siehe `taggenerator_lageretiketten/README.md`

## 📊 CSV-Format

```csv
Regal;Ebene;Fach;Barcode
R-001;01;4;1001014
R-001;01;3;1001013
R-001;01;2;1001012
R-001;01;1;1001011
```

**Spalten (automatisch erkannt):**
- `Regal` / `shelf`
- `Ebene` / `level`
- `Fach` / `slot` (1-4)
- `Barcode` / `barcode`

## 🎨 Output

Generierte PDFs:
- **Format:** A4-Querformat (4 Etiketten horizontal)
- **Pro Seite:** 1 Regal+Ebene-Kombination mit 4 Fächern (farbcodiert)
- **Pro Fach:** QR-Code + Barcode-Text + Fach-Nummer
- **Farben:** Fach 4=Gelb, 3=Orange, 2=Grün, 1=Blau

Beispiel: 600 Regal+Ebene-Kombinationen → 600 Seiten PDF

## ✨ Features

- ✅ Automatische Delimiter-Erkennung (`;`, `,`, `\t`)
- ✅ UTF-8 BOM-Handling
- ✅ Fehlertoleranz (fehlende Spalten → Fallback)
- ✅ Ressourcenschonend (serielles PDF-Rendering)
- ✅ Odoo Audit-Trail (optional, nachrüstbar)
- 🚀 API-ready für zukünftige Erweiterungen

## 📅 Roadmap

- [x] Phase 1: Standalone Python + Odoo GUI
- [ ] Phase 2: Odoo API-Integration (stock.location)
- [ ] Phase 3: Benutzerdefinierte Farb-/Layout-Profile
- [ ] Phase 4: Batch-History & Reports

## 📝 Git Commits

```
7b98813 Initial commit: Odoo Batch-Etikettengenerator
        - Python-Skript für PDF-Etikettengenerierung aus CSV
        - ReportLab für Vektor-Rendering mit Farbcodierung
        - Test-Daten mit 600 Regal+Ebene-Kombinationen
```

## 🆘 Support

**Fehler beim Standalone?**
- Prüfen Sie UTF-8 BOM in CSV
- Validieren Sie Spaltenköpfe

**Fehler im Odoo-Modul?**
- Form → Reiter "Fehlerinfo"
- Odoo Logs: Settings → Technical → Logs

---

**Autor:** Lager-IT  
**Lizenz:** LGPL-3  
**Version:** 1.0
