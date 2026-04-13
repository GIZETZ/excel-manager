# Module: excel_reader.py

import pandas as pd

def read_excel_file(file, sheet_name=0):
    """Lit un fichier Excel et retourne le DataFrame."""
    return pd.read_excel(file, sheet_name=sheet_name)

def detect_sheet_type(df):
    """Détecte si une feuille contient des sites ou des cellules."""
    cols_lower = [str(col).lower().strip() for col in df.columns]
    
    # Indicateurs de sites (données géographiques)
    site_indicators = {
        'mtn id': 2, 'id site': 2, 'code site': 2, 'code': 2,
        'lat': 2, 'latitude': 2,
        'long': 2, 'longitude': 2,
        'localit': 1, 'région': 1, 'ville': 1, 'nom site': 1, 'site name': 1,
    }
    
    # Indicateurs de cellules (paramètres techniques UMTS)
    cell_indicators = {
        'cell name': 2, 'cell id': 2, 'nom de cellule': 2, 'nom cellule': 2, 'cellule': 2,
        'dl primary': 2, 'downlink': 2, 'uarfcn': 2, 'dl code': 2, 'dl': 1,
        'nodeb': 2, 'nodeb name': 2, 'rrc id': 1, 'scrambling code': 2, 'scrambling': 2,
        'power': 1, 'transmit': 1, 'layer': 1
    }
    
    site_score = 0
    cell_score = 0
    
    # Calculer les scores
    for col in cols_lower:
        for ind, weight in site_indicators.items():
            if ind in col or col in ind:
                site_score += weight
                print(f"      Site match: '{col}' (weight {weight})")
    
    for col in cols_lower:
        for ind, weight in cell_indicators.items():
            if ind in col or col in ind:
                cell_score += weight
                print(f"      Cell match: '{col}' (weight {weight})")
    
    print(f"      Scores finaux: Site={site_score}, Cell={cell_score}")
    
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
        print(f"\n📋 Analyse feuille {sheet_idx} ({sheet_name}):")
        print(f"   - Taille: {len(df)} lignes, {len(df.columns)} colonnes")
        print(f"   - Colonnes: {list(df.columns)}")
        
        # Ignorer les feuilles vides
        if len(df) == 0 or len(df.columns) == 0:
            print(f"   ⚠️  Feuille vide, ignorée")
            continue
            
        sheet_type = detect_sheet_type(df)
        print(f"   - Type détecté: {sheet_type}")
        
        if sheet_type == 'sites' and sites_df is None:
            sites_df = df
            print(f"   ✅ Sites détectés: {len(sites_df)} lignes")
        elif sheet_type == 'cells' and cells_df is None:
            cells_df = df
            print(f"   ✅ Cellules détectées: {len(cells_df)} lignes")
        elif sheet_type == 'unknown':
            print(f"   ℹ️  Type inconnu - vérifier les colonnes")
    
    # Si les rôles sont encore indéterminés, utiliser la taille pour guider
    if sites_df is None or cells_df is None:
        print(f"\n⚠️  Attribution par défaut (fondée sur la taille)...")
        # Généralement, il y a plus de cellules que de sites
        all_dfs = [(pd.read_excel(xls, sheet_name=i), i, xls.sheet_names[i]) 
                   for i in range(len(xls.sheet_names)) 
                   if len(pd.read_excel(xls, sheet_name=i)) > 0]
        
        if len(all_dfs) > 0:
            sorted_dfs = sorted(all_dfs, key=lambda x: len(x[0]))
            
            if sites_df is None and len(sorted_dfs) >= 1:
                sites_df = sorted_dfs[0][0]
                print(f"   Sites assignés à feuille '{sorted_dfs[0][2]}' (plus petit: {len(sites_df)} lignes)")
            
            if cells_df is None and len(sorted_dfs) >= 2:
                cells_df = sorted_dfs[-1][0]
                print(f"   Cellules assignées à feuille '{sorted_dfs[-1][2]}' (plus grand: {len(cells_df)} lignes)")
            elif cells_df is None and len(sorted_dfs) == 1 and sites_df is None:
                # S'il n'y a qu'une feuille, l'utiliser pour les deux
                cells_df = sorted_dfs[0][0]
                print(f"   Cellules = Feuille unique '{sorted_dfs[0][2]}' ({len(cells_df)} lignes)")
    
    # Fallback final pour éviter les DataFrames vides
    if sites_df is None:
        print(f"\n⚠️  Aucun site détecté, utilisation feuille 0 par défaut")
        sites_df = pd.read_excel(xls, sheet_name=0) if len(xls.sheet_names) > 0 else pd.DataFrame()
    
    if cells_df is None:
        print(f"\n⚠️  Aucune cellule détectée, utilisation feuille 1 par défaut")
        cells_df = pd.read_excel(xls, sheet_name=1) if len(xls.sheet_names) > 1 else pd.DataFrame()
    
    print(f"\n✅ Résumé lecture:")
    print(f"   Sites: {len(sites_df)} lignes, {len(sites_df.columns)} colonnes")
    print(f"   Cellules: {len(cells_df)} lignes, {len(cells_df.columns)} colonnes")
    
    return sites_df, cells_df


def read_database_template(file_path):
    """Lit le template 2G3G4G_Cell Info.xlsx."""
    return file_path


def read_gsm_source(file_path):
    """Lit le fichier 2G GSM et retourne sites et cellules."""
    # Lire toutes les feuilles
    xls = pd.ExcelFile(file_path)
    print(f"📄 Feuilles détectées: {xls.sheet_names}")
    
    sites_df = None
    cells_df = None
    
    # Parcourir les feuilles et détecter le type
    for sheet_idx, sheet_name in enumerate(xls.sheet_names):
        df = pd.read_excel(xls, sheet_name=sheet_idx)
        print(f"\n📋 Analyse feuille {sheet_idx} ({sheet_name}):")
        print(f"   - Taille: {len(df)} lignes, {len(df.columns)} colonnes")
        print(f"   - Colonnes: {list(df.columns)[:5]}...")  # Afficher les 5 premières colonnes
        
        # Ignorer les feuilles vides
        if len(df) == 0 or len(df.columns) == 0:
            print(f"   ⚠️  Feuille vide, ignorée")
            continue
        
        # Détecter par présence de colonnes spécifiques
        cols_lower = [str(col).lower().strip() for col in df.columns]
        
        is_site = any('mtn' in col or 'latitude' in col or 'longitude' in col for col in cols_lower)
        is_gsm_cell = any('bts' in col or 'bsc' in col or 'local cell' in col for col in cols_lower)
        
        if is_site and sites_df is None:
            sites_df = df
            print(f"   ✅ Sites détectés: {len(sites_df)} lignes")
        elif is_gsm_cell and cells_df is None:
            cells_df = df
            print(f"   ✅ Cellules GSM détectées: {len(cells_df)} lignes")
    
    # Fallback par taille
    if sites_df is None or cells_df is None:
        print(f"\n⚠️  Attribution par défaut (fondée sur la taille)...")
        all_dfs = [(pd.read_excel(xls, sheet_name=i), i, xls.sheet_names[i]) 
                   for i in range(len(xls.sheet_names)) 
                   if len(pd.read_excel(xls, sheet_name=i)) > 0]
        
        if len(all_dfs) > 0:
            sorted_dfs = sorted(all_dfs, key=lambda x: len(x[0]))
            
            if sites_df is None and len(sorted_dfs) >= 1:
                sites_df = sorted_dfs[0][0]
                print(f"   Sites assignés à feuille '{sorted_dfs[0][2]}' (plus petit: {len(sites_df)} lignes)")
            
            if cells_df is None and len(sorted_dfs) >= 2:
                cells_df = sorted_dfs[-1][0]
                print(f"   Cellules assignées à feuille '{sorted_dfs[-1][2]}' (plus grand: {len(cells_df)} lignes)")
    
    # Fallback final
    if sites_df is None:
        print(f"\n⚠️  Aucun site détecté, utilisation feuille 0 par défaut")
        sites_df = pd.read_excel(xls, sheet_name=0) if len(xls.sheet_names) > 0 else pd.DataFrame()
    
    if cells_df is None:
        print(f"\n⚠️  Aucune cellule GSM détectée, utilisation feuille 1 par défaut")
        cells_df = pd.read_excel(xls, sheet_name=1) if len(xls.sheet_names) > 1 else pd.DataFrame()
    
    print(f"\n✅ Résumé lecture:")
    print(f"   Sites: {len(sites_df)} lignes, {len(sites_df.columns)} colonnes")
    print(f"   Cellules GSM: {len(cells_df)} lignes, {len(cells_df.columns)} colonnes")
    
    return sites_df, cells_df

