#!/usr/bin/env python3
import pandas as pd
import os

source = "network_excel_transformer/docs/UMTS CELL Info.xlsx"

if os.path.exists(source):
    print("=== COLONNES DU FICHIER SOURCE ===\n")
    
    print("📄 Feuille 1 (Sites):")
    df_sites = pd.read_excel(source, sheet_name=0)
    print(f"Colonnes: {list(df_sites.columns)}")
    print(f"Types: {list(df_sites.dtypes)}")
    print(f"Première ligne: {df_sites.iloc[0].to_dict() if len(df_sites) > 0 else 'vide'}")
    
    print("\n" + "="*50)
    print("\n📄 Feuille 2 (Cellules):")
    df_cells = pd.read_excel(source, sheet_name=1)
    print(f"Colonnes: {list(df_cells.columns)}")
    print(f"Types: {list(df_cells.dtypes)}")
    print(f"Première ligne: {df_cells.iloc[0].to_dict() if len(df_cells) > 0 else 'vide'}")
    
else:
    print(f"❌ Fichier non trouvé: {source}")
