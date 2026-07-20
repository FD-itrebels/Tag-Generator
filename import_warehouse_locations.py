#!/usr/bin/env python3
"""
Import Warehouse Locations from CSV into Odoo
Creates hierarchical structure: Warehouse → Regal → Ebene → Fach
"""
import csv
import os
import sys

# Lese CSV
csv_file = r'c:\Dev\taggenerator\odoo_export_test.csv'

locations = {}
regal_hierarchy = {}

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=';')
    
    for row in reader:
        regal = row['Regal'].strip()
        ebene = row['Ebene'].strip()
        fach = row['Fach'].strip()
        barcode = row['Barcode'].strip()
        
        # Hierarchie aufbauen
        if regal not in regal_hierarchy:
            regal_hierarchy[regal] = {}
        if ebene not in regal_hierarchy[regal]:
            regal_hierarchy[regal][ebene] = {}
        
        regal_hierarchy[regal][ebene][fach] = barcode

# Generate Odoo XML for import
xml_output = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <data noupdate="1">
'''

# Warehouse parent (aus Odoo Standard)
warehouse_id = 'stock.warehouse0'

# Root Location (LagerTest)
xml_output += f'''
    <!-- Root Location -->
    <record id="lageretiketten_root_location" model="stock.location">
      <field name="name">Lageretiketten Test Warehouse</field>
      <field name="location_id" ref="stock.stock_location_locations_partner"/>
      <field name="usage">internal</field>
      <field name="barcode">LAGER_ROOT_TEST</field>
    </record>
'''

# Generate Regal → Ebene → Fach Locations
for regal_name in sorted(regal_hierarchy.keys()):
    regal_id = f"lageretiketten_regal_{regal_name.replace('-', '_')}"
    
    # Regal Location
    xml_output += f'''
    <!-- Regal {regal_name} -->
    <record id="{regal_id}" model="stock.location">
      <field name="name">{regal_name}</field>
      <field name="location_id" ref="lageretiketten_root_location"/>
      <field name="usage">internal</field>
      <field name="barcode">{regal_name}</field>
    </record>
'''
    
    # Ebenen
    for ebene_name in sorted(regal_hierarchy[regal_name].keys()):
        ebene_id = f"lageretiketten_{regal_name.replace('-', '_')}_ebene_{ebene_name}"
        
        xml_output += f'''
    <!-- Regal {regal_name} - Ebene {ebene_name} -->
    <record id="{ebene_id}" model="stock.location">
      <field name="name">Ebene {ebene_name}</field>
      <field name="location_id" ref="{regal_id}"/>
      <field name="usage">internal</field>
      <field name="barcode">{regal_name}_{ebene_name}</field>
    </record>
'''
        
        # Fächer
        for fach_name in sorted(regal_hierarchy[regal_name][ebene_name].keys()):
            barcode = regal_hierarchy[regal_name][ebene_name][fach_name]
            fach_id = f"lageretiketten_{regal_name.replace('-', '_')}_ebene_{ebene_name}_fach_{fach_name}"
            
            xml_output += f'''
    <!-- Regal {regal_name} - Ebene {ebene_name} - Fach {fach_name} -->
    <record id="{fach_id}" model="stock.location">
      <field name="name">Fach {fach_name}</field>
      <field name="location_id" ref="{ebene_id}"/>
      <field name="usage">internal</field>
      <field name="barcode">{barcode}</field>
    </record>
'''

xml_output += '''
  </data>
</odoo>
'''

# Schreibe XML
output_file = r'c:\Dev\taggenerator\warehouse_import.xml'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(xml_output)

print(f"✅ Import XML generated: {output_file}")
print(f"   Regale: {len(regal_hierarchy)}")
total_faecher = sum(len(ebenen) * len(fach_dict) for ebenen_dict in regal_hierarchy.values() for ebenen, fach_dict in ebenen_dict.items())
print(f"   Total Fächer: {total_faecher}")
print(f"\n📋 Nächste Schritte:")
print(f"1. Datei in Odoo importieren:")
print(f"   - Lager → Konfiguration → Standorte → Importieren")
print(f"   - Oder: CLI via odoo-bin")
