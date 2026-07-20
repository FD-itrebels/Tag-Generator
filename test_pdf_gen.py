#!/usr/bin/env python
"""Test neue PDF-Generierung mit CSV Format"""
import sys
sys.path.insert(0, '.')

from taggenerator_lageretiketten.lib.pdf_generator import PDFLabelGenerator

generator = PDFLabelGenerator(label_width=410, label_height=70)
with open('warehouse_labels.csv', 'r', encoding='utf-8') as f:
    csv_content = f.read()

labels = generator.parse_csv_data(csv_content)
print(f'✅ {len(labels)} Labels gefunden')

# Test PDF Generierung
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
from collections import defaultdict
rack_count = defaultdict(int)
for label in labels:
    rack_count[label['rack']] += 1

for rack in sorted(rack_count.keys()):
    print(f'  {rack}: {rack_count[rack]} Labels')
