import sys
import os

print("Test des imports...")
try:
    sys.path.insert(0, 'network_excel_transformer')
    
    print("1. Import excel_reader...")
    from modules.excel_reader import read_umts_source
    print("   ✅ OK")
    
    print("2. Import transformer...")
    from modules.transformer import transform_site_data, transform_cell_data
    print("   ✅ OK")
    
    print("3. Import generator...")
    from modules.generator import generate_final_excel
    print("   ✅ OK")
    
    print("\n4. Lecture des fichiers source...")
    source_file = "network_excel_transformer/docs/UMTS CELL Info.xlsx"
    sites_raw, cells_raw = read_umts_source(source_file)
    print(f"   ✅ Sites: {len(sites_raw)} lignes")
    print(f"   ✅ Cellules: {len(cells_raw)} lignes")
    
    print("\n5. Transformation sites...")
    sites_t = transform_site_data(sites_raw)
    print(f"   ✅ Résultat: {len(sites_t)} lignes")
    
    print("\n6. Transformation cellules...")
    cells_t = transform_cell_data(cells_raw, sites_raw)
    print(f"   ✅ Résultat: {len(cells_t)} lignes")
    
    print("\n7. Génération fichier Excel...")
    db_file = "network_excel_transformer/docs/2G3G4G_Cell Info.xlsx"
    output = "network_excel_transformer/output/test_output.xlsx"
    result = generate_final_excel(sites_t, cells_t, db_file, output)
    print(f"   ✅ Fichier créé: {result}")
    
    if os.path.exists(output):
        size = os.path.getsize(output)
        print(f"   ✅ Taille fichier: {size} bytes")
        print("\n✅✅✅ TEST RÉUSSI ✅✅✅")
    else:
        print(f"   ❌ Fichier non trouvé: {output}")
        
except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
