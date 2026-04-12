#!/usr/bin/env python
# Script de test pour valider la transformation des données

import sys
sys.path.insert(0, 'network_excel_transformer')

from modules.excel_reader import read_umts_source
from modules.transformer import transform_site_data, transform_cell_data
from modules.generator import generate_final_excel
import os

print("=" * 60)
print("Test de transformation des données UMTS")
print("=" * 60)

try:
    # Chemins des fichiers
    source_file = "network_excel_transformer/docs/UMTS CELL Info.xlsx"
    db_file = "network_excel_transformer/docs/2G3G4G_Cell Info.xlsx"
    output_file = "network_excel_transformer/output/2G3G4G_Cell Info_filled.xlsx"
    
    # Vérifier que les fichiers existent
    if not os.path.exists(source_file):
        print(f"❌ Erreur : Fichier source non trouvé : {source_file}")
        sys.exit(1)
    
    if not os.path.exists(db_file):
        print(f"❌ Erreur : Fichier de base de données non trouvé : {db_file}")
        sys.exit(1)
    
    print(f"\n📖 Lecture du fichier source : {source_file}")
    sites_raw, cells_raw = read_umts_source(source_file)
    
    print(f"   ✅ Sites lus : {len(sites_raw)} lignes")
    print(f"   ✅ Cellules lues : {len(cells_raw)} lignes")
    
    print(f"\n⚙️  Transformation des sites...")
    sites_transformed = transform_site_data(sites_raw)
    print(f"   ✅ Sites transformés : {len(sites_transformed)} lignes")
    print(f"   Colonnes: {list(sites_transformed.columns)}")
    
    print(f"\n⚙️  Transformation des cellules...")
    cells_transformed = transform_cell_data(cells_raw, sites_raw)
    print(f"   ✅ Cellules transformées : {len(cells_transformed)} lignes")
    print(f"   Colonnes: {list(cells_transformed.columns)}")
    
    print(f"\n📝 Génération du fichier Excel final...")
    result_path = generate_final_excel(sites_transformed, cells_transformed, db_file, output_file)
    print(f"   ✅ Fichier généré : {result_path}")
    
    print(f"\n" + "=" * 60)
    print("✅ Transformation réussie!")
    print("=" * 60)
    print(f"\n📊 Résusmeé:")
    print(f"  - Sites générés: {len(sites_transformed)}")
    print(f"  - Cellules générées: {len(cells_transformed)}")
    print(f"  - Fichier de sortie: {output_file}")
    
except Exception as e:
    print(f"\n❌ Erreur lors de la transformation : {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
