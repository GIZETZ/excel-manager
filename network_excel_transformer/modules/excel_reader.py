# Module: excel_reader.py

import pandas as pd

def read_excel_file(file, sheet_name=0):
    """Lit un fichier Excel et retourne le DataFrame."""
    return pd.read_excel(file, sheet_name=sheet_name)

def detect_sheet_type(df):
    """Détecte si une feuille contient des sites ou des cellules."""
    cols_lower = [str(col).lower() for col in df.columns]
    
    # Indicateurs de sites (données géographiques)
    site_indicators = {
        'mtn id': 2, 'id site': 2, 'code site': 2,
        'lat': 2, 'latitude': 2,
        'long': 2, 'longitude': 2,
        'localit': 1, 'région': 1, 'ville': 1, 'nom site': 1
    }
    
    # Indicateurs de cellules (paramètres techniques UMTS)
    cell_indicators = {
        'cell name': 2, 'cell id': 2, 'nom de cellule': 2, 'nom cellule': 2,
        'dl primary': 2, 'downlink': 2, 'uarfcn': 2,
        'nodeb': 2, 'rrc id': 1, 'scrambling code': 2,
        'power': 1, 'transmit': 1
    }
    
    site_score = 0
    cell_score = 0
    
    # Calculer les scores
    for ind, weight in site_indicators.items():
        if any(ind in col for col in cols_lower):
            site_score += weight
            print(f"   Site indicator: {ind} (+{weight})")
    
    for ind, weight in cell_indicators.items():
        if any(ind in col for col in cols_lower):
            cell_score += weight
            print(f"   Cell indicator: {ind} (+{weight})")
    
    print(f"   Scores: Site={site_score}, Cell={cell_score}")
    
    if cell_score > site_score:
        return 'cells'
    elif site_score > cell_score:
        return 'sites'
    else:
        return 'unknown'

def read_umts_source(file_path):
    """Lit le fichier UMTS CELL Info.xls et retourne sites et cellules."""
    # Lire toutes les feuilles
    xls = pd.ExcelFile(file_path)
    print(f"📄 Feuilles détectées: {xls.sheet_names}")
    
    sites_df = None
    cells_df = None
    
    # Parcourir les feuilles et détecter le type
    for sheet_idx, sheet_name in enumerate(xls.sheet_names):
        df = pd.read_excel(xls, sheet_name=sheet_idx)
        sheet_type = detect_sheet_type(df)
        print(f"   Feuille {sheet_idx} ({sheet_name}): {sheet_type} - {len(df)} lignes, {len(df.columns)} colonnes")
        print(f"      Colonnes: {list(df.columns)[:5]}...")  # Afficher les 5 premières colonnes
        
        if sheet_type == 'sites' and sites_df is None:
            sites_df = df
            print(f"      ✅ Sites détectés: {len(sites_df)} lignes")
        elif sheet_type == 'cells' and cells_df is None:
            cells_df = df
            print(f"      ✅ Cellules détectées: {len(cells_df)} lignes")
    
    # Si les rôles sont encore indéterminés, utiliser la taille pour guider
    if sites_df is None or cells_df is None:
        # Généralement, il y a plus de cellules que de sites
        all_dfs = [(pd.read_excel(xls, sheet_name=i), i) for i in range(len(xls.sheet_names))]
        
        if sites_df is None or cells_df is None:
            # Assigner par taille : plus de lignes = cellules
            sorted_dfs = sorted(all_dfs, key=lambda x: len(x[0]))
            
            if sites_df is None and len(sorted_dfs) >= 1:
                sites_df = sorted_dfs[0][0]
                print(f"⚠️  Sites assignés à la feuille {sorted_dfs[0][1]} par défaut (plus petit)")
            
            if cells_df is None and len(sorted_dfs) >= 2:
                cells_df = sorted_dfs[-1][0]
                print(f"⚠️  Cellules assignées à la feuille {sorted_dfs[-1][1]} par défaut (plus grand)")
    
    # Fallback final
    if sites_df is None:
        sites_df = pd.read_excel(xls, sheet_name=0)
    if cells_df is None:
        cells_df = pd.read_excel(xls, sheet_name=1) if len(xls.sheet_names) > 1 else pd.DataFrame()
    
    return sites_df, cells_df

def read_database_template(file_path):
    """Lit le template 2G3G4G_Cell Info.xlsx."""
    return file_path


