#!/usr/bin/env python3
import os
import sys

print("Test d'imports de base...")
print(f"CWD: {os.getcwd()}")
print(f"Python: {sys.version}")

try:
    import pandas as pd
    print(f"✅ pandas {pd.__version__}")
except:
    print("❌ pandas non trouvé")

try:
    import openpyxl
    print(f"✅ openpyxl {openpyxl.__version__}")
except:
    print("❌ openpyxl non trouvé")

# Test des fichiers
source = "network_excel_transformer/docs/UMTS CELL Info.xlsx"
db = "network_excel_transformer/docs/2G3G4G_Cell Info.xlsx"

print(f"\nVérification des fichiers:")
print(f"Source existe: {os.path.exists(source)}")
print(f"DB existe: {os.path.exists(db)}")

if os.path.exists(source):
    try:
        df_sites = pd.read_excel(source, sheet_name=0)
        df_cells = pd.read_excel(source, sheet_name=1)
        print(f"✅ Lecture source: {len(df_sites)} sites, {len(df_cells)} cellules")
    except Exception as e:
        print(f"❌ Erreur lecture source: {e}")

print("\n✅ Test basique réussi")
