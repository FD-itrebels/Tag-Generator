#!/usr/bin/env python
"""Quick test of standalone script"""
import sys
sys.path.insert(0, '.')

from etikettendruck_standalone import PDFLabelGenerator

# Test
generator = PDFLabelGenerator(label_width=410, label_height=70)
with open('warehouse_labels.csv', 'r', encoding='utf-8') as f:
    csv_content = f.read()

labels = generator.parse_csv_data(csv_content)
print(f'✅ {len(labels)} Labels geparst')

pdf_buffer = generator.generate_pdf(labels)
with open('Warehouse_Labels_Standalone_Test.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

print(f'✅ PDF gespeichert: Warehouse_Labels_Standalone_Test.pdf')
print(f'✅ Slots: {len(labels) * 4}')
