#!/usr/bin/env python3
import csv

csv_file = r'c:\Dev\taggenerator\odoo_export_test.csv'
regal_hierarchy = {}

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        regal = row['Regal'].strip()
        ebene = row['Ebene'].strip()
        fach = row['Fach'].strip()
        barcode = row['Barcode'].strip()
        
        if regal not in regal_hierarchy:
            regal_hierarchy[regal] = {}
        if ebene not in regal_hierarchy[regal]:
            regal_hierarchy[regal][ebene] = {}
        
        regal_hierarchy[regal][ebene][fach] = barcode

# Generate XML
xml_output = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <data noupdate="1">

    <!-- Root Location (top-level view, no parent) -->
    <record id="lageretiketten_root_location" model="stock.location">
      <field name="name">Lageretiketten Test Warehouse</field>
      <field name="usage">view</field>
      <field name="barcode">LAGER_ROOT_TEST</field>
    </record>
'''

# Generate Regal → Ebene → Fach
for regal_name in sorted(regal_hierarchy.keys()):
    regal_id = f"lageretiketten_regal_{regal_name.replace('-', '_')}"
    xml_output += f'''
    <!-- Regal {regal_name} -->
    <record id="{regal_id}" model="stock.location">
      <field name="name">{regal_name}</field>
      <field name="location_id" ref="lageretiketten_root_location"/>
      <field name="usage">view</field>
      <field name="barcode">{regal_name}</field>
    </record>
'''
    
    for ebene_name in sorted(regal_hierarchy[regal_name].keys()):
        ebene_id = f"lageretiketten_{regal_name.replace('-', '_')}_ebene_{ebene_name}"
        xml_output += f'''
    <!-- Regal {regal_name} - Ebene {ebene_name} -->
    <record id="{ebene_id}" model="stock.location">
      <field name="name">Ebene {ebene_name}</field>
      <field name="location_id" ref="{regal_id}"/>
      <field name="usage">view</field>
      <field name="barcode">{regal_name}_{ebene_name}</field>
    </record>
'''
        
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

# Write output
output_file = r'c:\itrebels-dev\addons\taggenerator_lageretiketten\data\warehouse_import.xml'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(xml_output)

print("✅ XML regeneriert (ohne externe Referenzen)")
print(f"   Regale: {len(regal_hierarchy)}")
total = sum(len(ebenen) * len(fach_dict) for ebenen_dict in regal_hierarchy.values() for ebenen, fach_dict in ebenen_dict.items())
print(f"   Total Fächer: {total}")
