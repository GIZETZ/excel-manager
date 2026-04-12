# Module: generator.py

import pandas as pd
from openpyxl import load_workbook
import os

def generate_final_excel(site_df, cell_df, template_path, output_path):
    """Génère le fichier Excel final en ajoutant les données à la suite de la feuille 3G du template."""
    
    # Charger le workbook template
    wb = load_workbook(template_path)
    
    # Vérifier si la feuille 3G existe
    if '3G' in wb.sheetnames:
        ws = wb['3G']
        print(f"✅ Feuille 3G trouvée : {ws.max_row} lignes existantes")
    else:
        ws = wb.create_sheet('3G')
        print(f"✅ Nouvelle feuille 3G créée")
    
    # Déterminer la ligne de départ (après les données existantes)
    start_row = ws.max_row + 1
    if ws.max_row == 1:  # Feuille vide
        start_row = 1
    
    print(f"📝 Ajout des données à partir de la ligne {start_row}")
    
    # Écrire les données sites (Partie 1 - WCDMA_Site)
    row = start_row
    
    # Écrire les entêtes que si on commence à la ligne 1
    if start_row == 1:
        for col_idx, col_name in enumerate(site_df.columns, 1):
            ws.cell(row=row, column=col_idx, value=col_name)
        row += 1
        print(f"   Entête sites écrite à la ligne 1")
    
    # Données sites
    first_site_row = row
    for _, row_data in site_df.iterrows():
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=row, column=col_idx, value=value)
        row += 1
    print(f"   ✅ {len(site_df)} sites ajoutés (lignes {first_site_row}-{row-1})")
    
    # Ligne vide de séparation
    row += 1
    
    # Écrire les données cellules (Partie 2 - WCDMA_Cell)
    # Entête cellules
    first_cell_entete_row = row
    for col_idx, col_name in enumerate(cell_df.columns, 1):
        ws.cell(row=row, column=col_idx, value=col_name)
    row += 1
    
    # Données cellules
    first_cell_row = row
    for _, row_data in cell_df.iterrows():
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=row, column=col_idx, value=value)
        row += 1
    print(f"   ✅ {len(cell_df)} cellules ajoutées (lignes {first_cell_row}-{row-1})")
    
    # Sauvegarder le fichier
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    wb.save(output_path)
    print(f"✅ Fichier sauvegardé: {output_path}")
    
    return output_path

