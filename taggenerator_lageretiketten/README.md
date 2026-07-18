# Odoo 19 Lageretiketten-Modul

Custom Odoo-Modul zur Generierung farbcodierter Batch-PDF-Etiketten mit QR-Codes.

## Features

- ✅ CSV-Upload im Odoo-UI
- ✅ Automatische Delimiter-Erkennung
- ✅ Farbcodierte 4-in-1 Etiketten pro Regal+Ebene
- ✅ QR-Codes pro Lagerfach
- ✅ Audit-Trail (PDF-Speicherung optional)
- ✅ Responsive Odoo 19 UI (Form + List Views)
- 🚀 Vorbereitet für Odoo-API-Integration (Phase 2)

## Installation

### 1. Modul in Odoo.sh deployen

```bash
# Repository in odoo.sh konfigurieren
# Via Odoo.sh Dashboard: Settings → Repositories → Add "taggenerator"
# Branch: main
```

### 2. In Odoo App installieren

1. Odoo → Apps → "Lageretiketten" suchen
2. Installieren

### 3. Requirements

Das Modul installiert automatisch:
- `reportlab` (PDF-Rendering)

## Nutzung

### Schritt 1: Batch erstellen
Apps → Lageretiketten → Etikettenblöcke → Neu

### Schritt 2: CSV hochladen
- Hochladen im Format: `Regal;Ebene;Fach;Barcode`
- Beispiel:
  ```
  Regal;Ebene;Fach;Barcode
  R-001;01;4;001014001
  R-001;01;3;001013001
  R-001;01;2;001012001
  R-001;01;1;001011001
  ```

### Schritt 3: PDF generieren
- Button "🎨 PDF generieren" klicken
- Batch wird verarbeitet

### Schritt 4: Herunterladen
- Button "⬇️ PDF herunterladen" klicken
- PDF öffnet im Browser

## Konfiguration

### PDF-Speicherung (Audit-Trail)

Im Batch-Formular:
- ☑️ **PDF speichern** → Speichert PDF als Attachment (Audit-Trail aktiviert)
- ☐ **PDF speichern** → Stream-only (schneller, weniger Speicher)

## Fehlerbehandlung

Bei Problemen → Batch-Form → Reiter "Fehlerinfo"

## Erweiterte API (Phase 2)

Zukünftig:
- Direkter Zugriff auf `stock.location` aus Odoo Inventory
- Automatische CSV-Generierung aus Lagerdaten
- REST-Endpoint: `/label_batch/api/generate`

## Standalone-Nutzung

Das Projekt enthält auch ein reines Python-Script (`etikettendruck.py`), das unabhängig von Odoo läuft.

---
**Für Fragen oder Features:** Siehe README im Projekt-Root.
