# Label Layout Spezifikation (410×70mm, 4 Slots)

## Gesamt-Dimensionen
- **Breite**: 410mm
- **Höhe**: 70mm
- **Pro Slot**: 410/4 = 102.5mm breit

## Magenta Druck-Markierung
- **Border**: 5mm von allen Kanten (0.5cm)

## Pro Slot (102.5mm × 70mm)

### Layout von links nach rechts/oben nach unten:

| Element | Position X | Position Y | Größe | Font | Farbe | Bemerkung |
|---------|-----------|-----------|-------|------|-------|-----------|
| **RACK** (vertikal) | Slot_X + 3mm | 12mm | 16pt | Helvetica-Bold | Schwarz | Gedreht 90°, an linker Kante |
| **QR-Box** (weiß) | Slot_X + zentriert | ~60-62mm (oben) | 40×40mm + 1.5mm Padding | - | Weiß + grauer Border | Oben-Mitte, weiß hinterlegt |
| **QR-Code** | In QR-Box zentriert | In QR-Box zentriert | 40×40mm | - | Schwarz | Mittig in weißer Box |
| **SLOT-NUMMER** (4/3/2/1) | Slot_X + 97.5mm (rechts) | 62mm (oben) | 42pt | Helvetica-Bold | Schwarz | Oben-rechts |
| **BARCODE-TEXT** | Slot_X + 51.25mm (mitte) | 2mm (unten) | 20pt | Courier-Bold | Schwarz | Unten-center |
| **POSITION** (01/02/..) | Slot_X + 97.5mm (rechts) | 8mm (unten) | ?? pt | ?? | ?? | **FEHLT/UNKLAR - wo genau?** |

## Berechnungsbeispiel für Slot 1 (slot_index=0):
- Slot_X = 0 × 102.5 = 0mm
- Slot endet bei: 102.5mm

## Berechnungsbeispiel für Slot 4 (slot_index=3):
- Slot_X = 3 × 102.5 = 307.5mm
- Slot endet bei: 410mm

---

## FRAGEN FÜR USER:

1. **POSITION-TEXT (01, 02, etc.)**:
   - Wo soll das genau sein? (Position X und Y in mm)
   - Welche Fontgröße?
   - Gehört das ins Label oder war das ein Fehler?

2. **RACK-KENNUNG**:
   - Ist 16pt richtig oder sollte es größer/kleiner sein?
   - Position 3mm von links - stimmt das?

3. **SLOT-NUMMER**:
   - 42pt und 62mm von oben - passt das?
   - 97.5mm von links (rechter Rand) - richtig?

4. **QR-CODE & BOX**:
   - 40mm × 40mm + 1.5mm Padding - ok?
   - Position oben (~62mm) - richtig?

5. **BARCODE**:
   - Unten, 2mm Abstand - korrekt?
   - 20pt Courier - ok?
