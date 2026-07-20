import csv
from collections import defaultdict

# CSV lesen und auf relevante Felder reduzieren
input_file = 'Warehouse De Kwakel(Warehouse GPS).csv'
output_file = 'warehouse_labels.csv'

with open(input_file, 'r', encoding='utf-8') as f_in:
    reader = csv.DictReader(f_in)
    with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=['Level', 'Position', 'Barcode', 'Rack'])
        writer.writeheader()
        for row in reader:
            writer.writerow({
                'Level': row['Level'],
                'Position': row['Position'],
                'Barcode': row['Barcode'],
                'Rack': row['Rack']
            })

print('✅ warehouse_labels.csv erstellt')

# Statistik prüfen
labels_by_rack_pos = defaultdict(list)
with open(output_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row['Rack'], row['Position'])
        labels_by_rack_pos[key].append(row)

complete_labels = sum(1 for v in labels_by_rack_pos.values() if len(v) == 4)
print(f"📊 Eindeutige (Rack, Position) Paare: {len(labels_by_rack_pos)}")
print(f"📊 Labels mit allen 4 Levels: {complete_labels}")

# Rack-Statistik
rack_stats = defaultdict(lambda: {'positions': set(), 'total_rows': 0})
with open(output_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rack = row['Rack']
        rack_stats[rack]['positions'].add(row['Position'])
        rack_stats[rack]['total_rows'] += 1

for rack in sorted(rack_stats.keys()):
    stats = rack_stats[rack]
    pos_count = len(stats['positions'])
    print(f"  {rack}: {pos_count} Positionen × 4 Levels = {pos_count * 4} Zeilen (actual: {stats['total_rows']})")
