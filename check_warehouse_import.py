#!/usr/bin/env python3
"""
Check if warehouse locations were imported into Odoo
"""
import xmlrpc.client
import ssl

# Odoo.sh Zugangsdaten
url = "https://itrebels-dev-35098601.odoo.sh"
db = "itrebels-dev-35098601"
username = "admin@itrebels.de"  # ← ÄNDERE DAS
password = "DEIN_PASSWORT"      # ← ÄNDERE DAS

# SSL bypass (für dev)
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

try:
    # Connect
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("❌ Auth failed - check credentials")
        exit(1)
    
    # Query locations
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
    
    # Count total locations
    total_count = models.execute_kw(db, uid, password, 'stock.location', 'search_count', [])
    print(f"📊 Total Standorte in Odoo: {total_count}")
    
    # Find our test warehouse
    test_warehouse = models.execute_kw(db, uid, password, 'stock.location', 'search', 
                                        [['barcode', '=', 'LAGER_ROOT_TEST']])
    
    if test_warehouse:
        loc_id = test_warehouse[0]
        loc = models.execute_kw(db, uid, password, 'stock.location', 'read', [loc_id], 
                                 {'fields': ['name', 'barcode', 'usage', 'child_ids']})
        
        print(f"\n✅ Test Warehouse gefunden!")
        print(f"   Name: {loc[0]['name']}")
        print(f"   Barcode: {loc[0]['barcode']}")
        print(f"   Typ: {loc[0]['usage']}")
        print(f"   Child Locations: {len(loc[0]['child_ids'])}")
        
        # Check first Regal
        if loc[0]['child_ids']:
            regal_id = loc[0]['child_ids'][0]
            regal = models.execute_kw(db, uid, password, 'stock.location', 'read', 
                                      [regal_id], {'fields': ['name', 'barcode', 'child_ids']})
            print(f"\n   ├─ First Regal: {regal[0]['name']}")
            print(f"   │  Barcode: {regal[0]['barcode']}")
            print(f"   │  Child Ebenen: {len(regal[0]['child_ids'])}")
            
            # Check first Ebene
            if regal[0]['child_ids']:
                ebene_id = regal[0]['child_ids'][0]
                ebene = models.execute_kw(db, uid, password, 'stock.location', 'read', 
                                          [ebene_id], {'fields': ['name', 'barcode', 'child_ids']})
                print(f"      ├─ First Ebene: {ebene[0]['name']}")
                print(f"      │  Barcode: {ebene[0]['barcode']}")
                print(f"      │  Child Fächer: {len(ebene[0]['child_ids'])}")
                
                # Check first Fach
                if ebene[0]['child_ids']:
                    fach_id = ebene[0]['child_ids'][0]
                    fach = models.execute_kw(db, uid, password, 'stock.location', 'read', 
                                             [fach_id], {'fields': ['name', 'barcode', 'usage']})
                    print(f"         └─ First Fach: {fach[0]['name']}")
                    print(f"            Barcode: {fach[0]['barcode']}")
                    print(f"            Typ: {fach[0]['usage']}")
    else:
        print("❌ Test Warehouse NOT found - import may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTipps:")
    print("1. Benutzer/Passwort überprüfen")
    print("2. Sichere dich via Odoo.sh anmelden kannst")
    print("3. Schau in die Odoo logs")
