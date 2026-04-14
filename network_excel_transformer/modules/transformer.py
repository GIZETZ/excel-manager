# Module: transformer.py

import pandas as pd
import re

def calculate_azimuth(cell_name):
    """
    Calcule l'azimuth basé sur la dernière lettre/chiffre du nom de cellule.
    2G (terminaison 0,1,2): 0→0°, 1→120°, 2→240°
    3G (terminaison A-Z): A,J,S→0°; B,K,T→120°; C,L,U→240°; etc.
    """
    if pd.isna(cell_name):
        return None
    
    cell_str = str(cell_name).strip()
    if len(cell_str) == 0:
        return None
    
    last_char = cell_str[-1]
    
    # 2G: chiffre final
    if last_char.isdigit():
        digit = int(last_char)
        if digit == 0:
            return 0
        elif digit == 1:
            return 120
        elif digit == 2:
            return 240
        else:
            return None  # Cas non géré
    
    # 3G: lettre finale
    elif last_char.isalpha():
        letter_upper = last_char.upper()
        position = ord(letter_upper) - ord('A')  # 0-25
        azimuth_index = position % 3  # 0, 1, ou 2
        
        if azimuth_index == 0:
            return 0
        elif azimuth_index == 1:
            return 120
        else:  # azimuth_index == 2
            return 240
    
    return None


def calculate_azimuth_lte(cell_name):
    """
    Calcule l'azimuth pour 4G LTE basé sur la première lettre du suffixe.
    T, W, W1-W3, Z0-Z2 → 0°
    U, X, X1-X3 → 120°
    V, Y, Y1-Y3 → 240°
    Pattern: T (0°) → U (120°) → V (240°) → W (0°) → X (120°) → Y (240°) → Z (0°)
    """
    if pd.isna(cell_name):
        return None
    
    cell_str = str(cell_name).strip()
    if len(cell_str) == 0:
        return None
    
    # Extraire le suffixe après le dernier tiret
    if '_' in cell_str:
        suffix = cell_str.split('_')[-1]
    else:
        suffix = cell_str
    
    if len(suffix) == 0:
        return None
    
    # Obtenir la première lettre du suffixe
    first_letter = suffix[0].upper()
    
    # Mapping basé sur la position relative à T
    # T=0, U=1, V=2, W=3, X=4, Y=5, Z=6, etc.
    if first_letter < 'T':
        # Lettres avant T: A, B, C, ..., S - on utilise la logique 3G
        position = ord(first_letter) - ord('A')
        azimuth_index = position % 3
        return [0, 120, 240][azimuth_index]
    else:
        # Lettres T et après: utiliser la position relative à T
        position = ord(first_letter) - ord('T')
        azimuth_index = position % 3
        return [0, 120, 240][azimuth_index]


def find_matching_column(df, possible_names):
    """Trouve une colonne dans le DataFrame en testant plusieurs noms possibles."""
    for col in df.columns:
        if col.strip() in possible_names:
            return col
        if col.strip().lower() in [name.lower() for name in possible_names]:
            return col
    return None

def extract_numbers_from_text(text):
    """Extrait tous les nombres d'un texte (entiers et décimaux)."""
    if pd.isna(text):
        return 'N/A'
    
    text_str = str(text).strip()
    if len(text_str) == 0:
        return 'N/A'
    
    # Extraire tous les nombres (entiers et décimaux avec point)
    numbers = re.findall(r'\d+(?:\.\d+)?', text_str)
    
    if numbers:
        # Retourner les nombres séparés par un slash si plusieurs
        return ' / '.join(numbers)
    else:
        return text_str  # Retourner le texte original s'il n'y a pas de nombres

def transform_site_data(df):
    """Transforme les données de site selon les correspondances UMTS vers DB (3G)."""
    # Afficher les colonnes réelles pour debug
    print(f"🔍 Colonnes du fichier source (sites): {list(df.columns)}")
    df = df.copy()
    
    # Mappings flexibles pour chaque colonne
    mtn_id_col = find_matching_column(df, ['MTN ID', 'MTN_ID', 'code', 'CI', 'code site'])
    mtn_name_col = find_matching_column(df, ['MTN Name', 'MTN_Name', 'name', 'nom', 'site name', 'Nom site'])
    lat_col = find_matching_column(df, ['Lat', 'Latitude', 'lat'])
    long_col = find_matching_column(df, ['Long', 'Longitude', 'long'])
    
    print(f"Colonnes détectées: MTN ID={mtn_id_col}, MTN Name={mtn_name_col}, Lat={lat_col}, Long={long_col}")
    
    # Si on n'a pas les colonnes de sites, retourner DataFrame vide pour signaler
    if not all([mtn_id_col, mtn_name_col, lat_col, long_col]):
        print(f"⚠️  Colonnes de sites non trouvées. Présentes: {list(df.columns)}")
        # Retourner un DataFrame vide avec les bonnes colonnes
        return pd.DataFrame(columns=['WCDMA_Site', 'nom site', 'code site', 'lat', 'long'])
    
    # Renommer en colonnes cibles
    df = df[[mtn_id_col, mtn_name_col, lat_col, long_col]].copy()
    df.columns = ['code site', 'nom site', 'lat', 'long']
    
    # Ajouter le préfixe 3G_ au nom site
    df['nom site'] = '3G_' + df['nom site'].astype(str)
    
    # Ajouter la colonne WCDMA_Site
    df['WCDMA_Site'] = 'WCDMA_Site'
    
    # Réorganiser les colonnes pour l'export
    cols = ['WCDMA_Site', 'nom site', 'code site', 'lat', 'long']
    return df[cols]


def transform_gsm_site_data(df):
    """Transforme les données de site selon les correspondances GSM vers DB (2G)."""
    # Afficher les colonnes réelles pour debug
    print(f"🔍 Colonnes du fichier source (sites 2G): {list(df.columns)}")
    df = df.copy()
    
    # Mappings flexibles pour chaque colonne
    mtn_id_col = find_matching_column(df, ['MTN ID', 'MTN_ID', 'code', 'CI', 'code site'])
    mtn_name_col = find_matching_column(df, ['MTN Name', 'MTN_Name', 'name', 'nom', 'site name', 'Nom site'])
    lat_col = find_matching_column(df, ['Lat', 'Latitude', 'lat'])
    long_col = find_matching_column(df, ['Long', 'Longitude', 'long'])
    
    print(f"Colonnes détectées: MTN ID={mtn_id_col}, MTN Name={mtn_name_col}, Lat={lat_col}, Long={long_col}")
    
    # Si on n'a pas les colonnes de sites, retourner DataFrame vide
    if not all([mtn_id_col, mtn_name_col, lat_col, long_col]):
        print(f"⚠️  Colonnes de sites non trouvées. Présentes: {list(df.columns)}")
        return pd.DataFrame(columns=['GSM_Site', 'nom site', 'code site', 'lat', 'long'])
    
    # Renommer en colonnes cibles
    df = df[[mtn_id_col, mtn_name_col, lat_col, long_col]].copy()
    df.columns = ['code site', 'nom site', 'lat', 'long']
    
    # Ajouter le préfixe 2G_ au nom site (GSM 2G)
    df['nom site'] = '2G_' + df['nom site'].astype(str)
    
    # Ajouter la colonne GSM_Site
    df['GSM_Site'] = 'GSM_Site'
    
    # Réorganiser les colonnes pour l'export
    cols = ['GSM_Site', 'nom site', 'code site', 'lat', 'long']
    return df[cols]


def extract_code_site_from_nodeb_name(nodeb_name):
    """Extrait le code site du nom NodeB (ex: 3G_CI00001_Abengourou1 -> CI00001)."""
    if pd.isna(nodeb_name):
        return None
    match = re.search(r'CI\d{5}', str(nodeb_name))
    if match:
        return match.group()
    return None

def extract_city_name_from_cell(cell_name):
    """Extrait le nom de la ville du Cell Name (avant le tiret)."""
    if pd.isna(cell_name):
        return None
    cell_str = str(cell_name).strip()
    # Prend la partie avant le premier tiret
    if '-' in cell_str:
        return cell_str.split('-')[0].strip()
    return cell_str


def detect_cell_type(df):
    """Détecte si les cellules sont 2G GSM, 3G UMTS ou 4G LTE basé sur les colonnes."""
    cols_lower = [str(col).lower().strip() for col in df.columns]
    
    # Indicateurs 3G UMTS
    umts_indicators = ['nodeb', 'uarfcn', 'downlink', 'scrambling', 'dl primary', 'dl code']
    
    # Indicateurs 2G GSM
    gsm_indicators = ['bts', 'bsc', 'bcch', 'gsm', 'trx']
    
    # Indicateurs 4G LTE
    lte_indicators = ['enodeb', 'earfcn', 'physical cell id', 'local cell identity']
    
    umts_score = sum(1 for ind in umts_indicators if any(ind in col for col in cols_lower))
    gsm_score = sum(1 for ind in gsm_indicators if any(ind in col for col in cols_lower))
    lte_score = sum(1 for ind in lte_indicators if any(ind in col for col in cols_lower))
    
    print(f"\n📊 Détection du type de cellules:")
    print(f"   Score UMTS 3G: {umts_score}")
    print(f"   Score GSM 2G: {gsm_score}")
    print(f"   Score LTE 4G: {lte_score}")
    
    if lte_score > gsm_score and lte_score > umts_score:
        print(f"   ✅ Fichier LTE 4G détecté!")
        return "LTE"
    elif gsm_score > umts_score:
        print(f"   ✅ Fichier GSM 2G détecté!")
        return "GSM"
    else:
        print(f"   ✅ Fichier UMTS 3G détecté")
        return "UMTS"


def transform_cell_data(df, site_df_raw):
    """Détecte automatiquement 2G ou 3G et route vers la bonne fonction."""
    cell_type = detect_cell_type(df)
    
    if cell_type == "LTE":
        print(f"\n✅ Fichier LTE 4G détecté!")
        print(f"   Utilisation de transform_lte_cell_data()")
        return transform_lte_cell_data(df, site_df_raw)
    elif cell_type == "GSM":
        print(f"\n✅ Fichier GSM 2G détecté!")
        print(f"   Utilisation de transform_gsm_cell_data()")
        return transform_gsm_cell_data(df, site_df_raw)
    else:
        # Fichier 3G UMTS normal
        return _transform_cell_data_umts(df, site_df_raw)


def _transform_cell_data_umts(df, site_df_raw):
    
    # Vérifier si DataFrame vide
    if len(df) == 0 or len(df.columns) == 0:
        print(f"⚠️  WARNING: DataFrame cellules est VIDE!")
        print(f"   - Nombre de lignes: {len(df)}")
        print(f"   - Nombre de colonnes: {len(df.columns)}")
        raise ValueError(
            f"❌ Le fichier des cellules est VIDE ou mal détecté!\n"
            f"   Vérifiez que vous avez importé le bon fichier source avec les deux feuilles"
            f" (sites ET cellules).\n"
            f"   Colonnes trouvées: {list(df.columns)}"
        )
    
    df = df.copy()
    
    # Mappings flexibles pour chaque colonne
    cell_name_col = find_matching_column(df, ['Cell Name', 'Cell_Name', 'cellule', 'cell'])
    dl_prim_col = find_matching_column(df, ['DL Primary Scrambling Code', 'DL_Primary_Scrambling_Code', 'cellId', 'code', 'dl code', 'dl', 'scrambling'])
    downlink_col = find_matching_column(df, ['Downlink UARFCN', 'Downlink_UARFCN', 'Layer_type', 'layer', 'uarfcn'])
    nodeb_col = find_matching_column(df, ['NodeB Name', 'NodeB_Name', 'nodeb', 'name'])
    
    print(f"Colonnes détectées: Cell Name={cell_name_col}, DL Prim={dl_prim_col}, Downlink={downlink_col}, NodeB={nodeb_col}")
    
    if not all([cell_name_col, dl_prim_col, downlink_col, nodeb_col]):
        missing = []
        if not cell_name_col: missing.append("Cell Name (cellule)")
        if not dl_prim_col: missing.append("DL Primary/Code")
        if not downlink_col: missing.append("Downlink/Layer/UARFCN")
        if not nodeb_col: missing.append("NodeB Name")
        
        raise ValueError(
            f"❌ Colonnes requises non trouvées!\n"
            f"   Colonnes manquantes: {', '.join(missing)}\n"
            f"   Colonnes trouvées: {list(df.columns)}\n"
            f"   Vérifiez que le fichier source contient les cellules dans une feuille avec les bonnes en-têtes."
        )
    
    # Sélectionner et renommer les colonnes nécessaires
    df_selected = df[[cell_name_col, dl_prim_col, downlink_col, nodeb_col]].copy()
    df_selected.columns = ['nom cellule', 'cellId', 'Layer_type', 'NodeB Name']
    
    # Extraire le nom de ville du Cell Name (avant le tiret)
    df_selected['nom_ville'] = df_selected['nom cellule'].apply(extract_city_name_from_cell)
    print(f"❔ Noms de villes extraits des cellules: {df_selected['nom_ville'].unique()}")
    
    # Extraire le code site du NodeB Name
    df_selected['code site'] = df_selected['NodeB Name'].apply(extract_code_site_from_nodeb_name)
    print(f"❔ Codes sites extraits: {df_selected['code site'].unique()}")
    
    # Créer un mapping site: code site + nom site
    site_mapping = site_df_raw[['MTN ID', 'MTN Name']].copy()
    site_mapping.columns = ['code site', 'MTN Name']
    site_mapping['nom_ville_site'] = site_mapping['MTN Name'].astype(str).str.strip().str.lower()
    site_mapping['nom site'] = '3G_' + site_mapping['MTN Name'].astype(str)
    print(f"\n📍 Mapping sites disponibles:")
    print(f"   Codes sites: {site_mapping['code site'].unique()}")
    print(f"   Noms de villes (sites): {site_mapping['nom_ville_site'].unique()}")
    
    # Normaliser les noms de villes des cellules pour la comparaison
    df_selected['nom_ville_normalized'] = df_selected['nom_ville'].astype(str).str.strip().str.lower()
    
    # Créer un mapping complet avec MTN Name non-normalisé
    site_mapping_full = site_df_raw[['MTN ID', 'MTN Name']].copy()
    site_mapping_full.columns = ['code site', 'MTN Name']
    site_mapping_full['MTN Name_normalized'] = site_mapping_full['MTN Name'].astype(str).str.strip().str.lower()
    site_mapping_full['nom site'] = '3G_' + site_mapping_full['MTN Name'].astype(str)
    
    # Fusion principale: Par nom de ville (Cell Name prefix = MTN Name)
    print(f"\n🔗 Fusion par MTN NAME (Vérification: Cell Name prefix = MTN Name)...")
    df_merged = df_selected.merge(
        site_mapping_full[['MTN Name', 'MTN Name_normalized', 'code site', 'nom site']], 
        left_on='nom_ville_normalized', 
        right_on='MTN Name_normalized',
        how='left',
        suffixes=('_cell', '_site')
    )
    
    # Utiliser la colonne code site du site (pas celle du NodeB)
    if 'code site_site' in df_merged.columns:
        df_merged['code site'] = df_merged['code site_site']
        df_merged = df_merged.drop(columns=['code site_cell', 'code site_site'])
    
    # Vérification: Cell Name prefix == MTN Name du site
    print(f"\n✅ VÉRIFICATION DES CORRESPONDANCES:")
    
    valid_cells = df_merged[df_merged['nom site'].notna()].copy()
    if len(valid_cells) > 0:
        print(f"\n📋 Cellules VALIDÉES ({len(valid_cells)}):")
        matches_ok = 0
        for idx, row in valid_cells.iterrows():
            cell_name_prefix = row['nom_ville'].strip().lower()
            mtn_name = row['MTN Name'].strip().lower()
            match = cell_name_prefix == mtn_name
            if match:
                matches_ok += 1
                print(f"   ✅ {row['nom cellule']:20s} → {row['MTN Name']:20s} (OK)")
            else:
                print(f"   ❌ {row['nom cellule']:20s} → {row['MTN Name']:20s} (MISMATCH)")
        
        print(f"\n   Résultat: {matches_ok}/{len(valid_cells)} correspondances correctes")
        
        # Garder seulement les cellules qui matchent
        df_merged = valid_cells[valid_cells.apply(lambda row: row['nom_ville'].strip().lower() == row['MTN Name'].strip().lower(), axis=1)].copy()
        print(f"\n✅ {len(df_merged)} cellules conservées après vérification")
    
    # Supprimer les cellules orphelines (pas de matching)
    orphaned = df_selected[~df_selected.index.isin(df_merged.index)]
    if len(orphaned) > 0:
        print(f"\n⚠️  {len(orphaned)} cellules ORPHELINES SUPPRIMÉES (pas de MTN Name correspondant):")
        for idx, row in orphaned.iterrows():
            print(f"   🗑️  {row['nom cellule']:20s} | Ville extraite: {row['nom_ville']}")
    
    # Ajouter la colonne WCDMA_Cell
    df_merged['WCDMA_Cell'] = 'WCDMA_Cell'
    
    # Calculer l'azimuth basé sur la dernière lettre du nom de cellule
    df_merged['azimuth'] = df_merged['nom cellule'].apply(calculate_azimuth)
    print(f"\n📐 Azimuth calculés : {df_merged['azimuth'].value_counts().to_dict()}")
    
    # Colonnes nécessaires pour la feuille 3G (avec azimuth)
    cols = ['WCDMA_Cell', 'code site', 'nom cellule', 'cellId', 'Layer_type', 'azimuth']
    result = df_merged[cols].copy()

    
    # 🔤 TRIER PAR SITE PUIS NOM DE CELLULE
    result = result.sort_values(['code site', 'nom cellule']).reset_index(drop=True)
    
    print(f"\n✅ Transformation cellules: {len(result)} lignes (triées par site)")
    return result


def extract_code_site_from_bts_name(bts_name):
    """Extrait le code site du nom BTS 2G (ex: 2G_CI02693_Lahoudigan -> CI02693)."""
    if pd.isna(bts_name):
        return None
    match = re.search(r'CI\d{5}', str(bts_name))
    if match:
        return match.group()
    return None


def transform_gsm_cell_data(df, site_df_raw):
    """Transforme les données de cellule GSM 2G et les fusionne avec les sites."""
    print(f"🔍 Colonnes du fichier source (cellules GSM 2G): {list(df.columns)}")
    
    # Vérifier si DataFrame vide
    if len(df) == 0 or len(df.columns) == 0:
        raise ValueError(
            f"❌ Le fichier des cellules GSM est VIDE ou mal détecté!\n"
            f"   Colonnes trouvées: {list(df.columns)}"
        )
    
    df = df.copy()
    
    # Mappings flexibles pour les colonnes GSM 2G
    cell_name_col = find_matching_column(df, ['Cell Name', 'Cell_Name', 'cellule', 'cell'])
    cell_id_col = find_matching_column(df, ['Cell ID', 'Cell_ID', 'cell id', 'cellId'])
    bts_name_col = find_matching_column(df, ['BTS Name', 'BTS_Name', 'bts', 'bts name'])
    bcch_freq_col = find_matching_column(df, ['BCCH Frequency', 'BCCH_Frequency', 'bcch', 'frequency'])
    # Ajouter les colonnes Cell CI et Freq. Band
    cell_ci_col = find_matching_column(df, ['Cell CI', 'Cell_CI', 'cell ci', 'cell_ci'])
    freq_band_col = find_matching_column(df, ['Freq. Band', 'Freq Band', 'Frequency Band', 'freq band', 'frequency band'])
    
    print(f"Colonnes détectées: Cell Name={cell_name_col}, Cell ID={cell_id_col}, BTS Name={bts_name_col}, BCCH={bcch_freq_col}, Cell CI={cell_ci_col}, Freq. Band={freq_band_col}")
    
    if not all([cell_name_col, cell_id_col, bts_name_col]):
        missing = []
        if not cell_name_col: missing.append("Cell Name")
        if not cell_id_col: missing.append("Cell ID")
        if not bts_name_col: missing.append("BTS Name")
        
        raise ValueError(
            f"❌ Colonnes requises non trouvées pour GSM 2G!\n"
            f"   Colonnes manquantes: {', '.join(missing)}\n"
            f"   Colonnes trouvées: {list(df.columns)}"
        )
    
    # Sélectionner et renommer les colonnes
    cols_to_select = [cell_name_col, cell_id_col, bts_name_col]
    df_selected = df[cols_to_select].copy()
    df_selected.columns = ['nom cellule', 'cellId', 'BTS Name']
    
    # Ajouter BCCH Frequency si trouvée
    if bcch_freq_col:
        df_selected['BCCH Frequency'] = df[bcch_freq_col].values
    else:
        df_selected['BCCH Frequency'] = 'N/A'
    
    # Ajouter Cell CI si trouvée
    if cell_ci_col:
        df_selected['Cell CI'] = df[cell_ci_col].values
        print(f"   ✅ Colonne 'Cell CI' ajoutée")
    else:
        df_selected['Cell CI'] = 'N/A'
        print(f"   ⚠️  Colonne 'Cell CI' non trouvée")
    
    # Ajouter Freq. Band si trouvée
    if freq_band_col:
        df_selected['Freq. Band'] = df[freq_band_col].apply(extract_numbers_from_text)
        print(f"   ✅ Colonne 'Freq. Band' ajoutée (nombres extraits)")
    else:
        df_selected['Freq. Band'] = 'N/A'
        print(f"   ⚠️  Colonne 'Freq. Band' non trouvée")
    
    # Extraire le nom de ville du Cell Name (avant le tiret)
    df_selected['nom_ville'] = df_selected['nom cellule'].apply(extract_city_name_from_cell)
    print(f"❔ Noms de villes extraits des cellules: {df_selected['nom_ville'].unique()}")
    
    # Extraire le code site du BTS Name
    df_selected['code site'] = df_selected['BTS Name'].apply(extract_code_site_from_bts_name)
    print(f"❔ Codes sites extraits: {df_selected['code site'].unique()}")
    
    # Créer un mapping complet avec MTN Name non-normalisé
    site_mapping_full = site_df_raw[['MTN ID', 'MTN Name']].copy()
    site_mapping_full.columns = ['code site', 'MTN Name']
    site_mapping_full['MTN Name_normalized'] = site_mapping_full['MTN Name'].astype(str).str.strip().str.lower()
    site_mapping_full['nom site'] = '2G_' + site_mapping_full['MTN Name'].astype(str)
    
    print(f"\n📍 Mapping sites disponibles (par MTN Name):")
    print(f"   MTN Names: {site_mapping_full['MTN Name'].unique()}")
    
    # Normaliser les noms de villes
    df_selected['nom_ville_normalized'] = df_selected['nom_ville'].astype(str).str.strip().str.lower()
    
    # Fusion principale: Par nom de ville (Cell Name prefix = MTN Name)
    print(f"\n🔗 Fusion par MTN NAME (Vérification: Cell Name prefix = MTN Name)...")
    df_merged = df_selected.merge(
        site_mapping_full[['MTN Name', 'MTN Name_normalized', 'code site', 'nom site']], 
        left_on='nom_ville_normalized', 
        right_on='MTN Name_normalized',
        how='left',
        suffixes=('', '_site')
    )
    
    # Renommer 'code site_site' en 'code site' (du site)
    if 'code site_site' in df_merged.columns:
        df_merged['code site'] = df_merged['code site_site']
        df_merged = df_merged.drop(columns=['code site_site'])
    
    # Vérification: Cell Name prefix == MTN Name du site
    print(f"\n✅ VÉRIFICATION DES CORRESPONDANCES GSM 2G:")
    
    valid_cells = df_merged[df_merged['nom site'].notna()].copy()
    if len(valid_cells) > 0:
        print(f"\n📋 Cellules VALIDÉES ({len(valid_cells)}):")
        matches_ok = 0
        for idx, row in valid_cells.iterrows():
            cell_name_prefix = row['nom_ville'].strip().lower()
            mtn_name = row['MTN Name'].strip().lower()
            match = cell_name_prefix == mtn_name
            if match:
                matches_ok += 1
                print(f"   ✅ {row['nom cellule']:20s} → {row['MTN Name']:20s} (OK)")
            else:
                print(f"   ❌ {row['nom cellule']:20s} → {row['MTN Name']:20s} (MISMATCH)")
        
        print(f"\n   Résultat: {matches_ok}/{len(valid_cells)} correspondances correctes")
        
        # Garder seulement les cellules qui matchent
        df_merged = valid_cells[valid_cells.apply(lambda row: row['nom_ville'].strip().lower() == row['MTN Name'].strip().lower(), axis=1)].copy()
        print(f"\n✅ {len(df_merged)} cellules GSM conservées après vérification")
    
    # Calculer l'azimuth basé sur la dernière chiffre du nom de cellule
    df_merged['azimuth'] = df_merged['nom cellule'].apply(calculate_azimuth)
    print(f"\n📐 Azimuth calculés GSM : {df_merged['azimuth'].value_counts().to_dict()}")
    
    # Colonnes finales (avec azimuth, Cell CI et Freq. Band)
    cols = ['GSM_Cell', 'code site', 'nom cellule', 'cellId', 'BCCH Frequency', 'Cell CI', 'Freq. Band', 'azimuth']
    df_merged['GSM_Cell'] = 'GSM_Cell'
    result = df_merged[cols].copy()
    
    # Trier par site puis par nom (cohérent avec 3G)
    result = result.sort_values(['code site', 'nom cellule']).reset_index(drop=True)
    
    print(f"\n✅ Transformation cellules GSM: {len(result)} lignes (triées par site)")
    return result


def transform_lte_site_data(df):
    """Transforme les données de site 4G LTE. Utilise Lat/Long comme identifiant UNIQUE comme pour 2G/3G."""
    print(f"🔍 Colonnes du fichier source (sites LTE 4G): {list(df.columns)}")
    
    # Chercher les colonnes de sites LTE
    lat_col = find_matching_column(df, ['Lat', 'Latitude', 'lat'])
    long_col = find_matching_column(df, ['Long', 'Longitude', 'long'])
    ne_name_col = find_matching_column(df, ['NE Name', 'ne name', 'eNodeB Name', 'enodeb name'])
    # Chercher les colonnes MTN ID (code site) et MTN Name (nom du site) comme pour 2G/3G
    mtn_id_col = find_matching_column(df, ['MTN ID', 'MTN_ID', 'mtn id', 'mtn_id', 'code site', 'code_site'])
    site_name_col = find_matching_column(df, ['MTN Name', 'Site Name', 'site name', 'site_name', 'nom site', 'nom_site', 'name'])
    
    print(f"Colonnes détectées: MTN ID={mtn_id_col}, Site Name={site_name_col}, Lat={lat_col}, Long={long_col}, NE Name={ne_name_col}")
    
    # Stratégie 1: Si on a lat/long, c'est la source de vérité (comme 2G/3G)
    if lat_col and long_col:
        print(f"✅ Données géographiques trouvées (Lat/Long) - Utilisation comme clé unique")
        # Deduuplicate par lat+long (chaque combinaison = 1 site)
        cols_to_keep = [lat_col, long_col]
        if mtn_id_col:
            cols_to_keep.insert(0, mtn_id_col)
        if site_name_col:
            cols_to_keep.insert(0, site_name_col)
        if ne_name_col and mtn_id_col is None:
            cols_to_keep.insert(0, ne_name_col)
        
        df_sites = df[cols_to_keep].drop_duplicates().copy()
        print(f"   Sites uniques par (Lat, Long): {len(df_sites)}")
        
        # Créer le code site: utiliser MTN ID si disponible, sinon NE Name, sinon index
        if mtn_id_col:
            df_sites['code site'] = df_sites[mtn_id_col].astype(str)
            print(f"   Code site depuis MTN ID")
        elif ne_name_col:
            df_sites['code site'] = df_sites[ne_name_col].astype(str).apply(lambda x: x.split('_')[0] if '_' in str(x) else x)
            print(f"   Code site depuis NE Name")
        else:
            df_sites['code site'] = range(len(df_sites))
            print(f"   Code site auto-incrémenté")
        
        # Utiliser la colonne MTN Name (Site Name) si disponible, sinon générer depuis NE Name
        if site_name_col:
            df_sites['nom site'] = '4G_' + df_sites[site_name_col].astype(str)
            print(f"   Nom site depuis MTN Name")
        elif ne_name_col:
            df_sites['nom_site_base'] = df_sites[ne_name_col].astype(str).apply(lambda x: x.split('_')[1] if '_' in str(x) and len(str(x).split('_')) > 1 else str(x))
            df_sites['nom site'] = '4G_' + df_sites['nom_site_base'].astype(str)
            print(f"   Nom site depuis NE Name")
        else:
            df_sites['nom site'] = '4G_Site_' + df_sites['code site'].astype(str)
            print(f"   Nom site génériques")
        
        df_sites['LTE_Site'] = 'LTE_Site'
        cols = ['LTE_Site', 'nom site', 'code site', lat_col, long_col]
        result = df_sites[cols].reset_index(drop=True).copy()
        result.columns = ['LTE_Site', 'nom site', 'code site', 'lat', 'long']
        
    else:
        # Stratégie 2: Sinon, extraire les sites uniques de NE Name (fallback)
        print(f"⚠️  Pas de Lat/Long trouvées. Utilisation NE Name comme fallback...")
        
        if ne_name_col:
            df_ne = df[[ne_name_col]].copy()
            df_ne.columns = ['NE Name full']
            df_ne['code site'] = df_ne['NE Name full'].astype(str).apply(lambda x: x.split('_')[0] if '_' in str(x) else x)
            df_ne['nom_site_base'] = df_ne['NE Name full'].astype(str).apply(lambda x: x.split('_')[1] if '_' in str(x) and len(str(x).split('_')) > 1 else str(x))
            df_ne['nom site'] = '4G_' + df_ne['nom_site_base'].astype(str)
            df_ne['LTE_Site'] = 'LTE_Site'
            cols = ['LTE_Site', 'nom site', 'code site']
            result = df_ne[cols].drop_duplicates().reset_index(drop=True).copy()
        else:
            print(f"❌ Impossible de créer les sites: NE Name non trouvé")
            result = pd.DataFrame(columns=['LTE_Site', 'nom site', 'code site'])
    
    print(f"\n✅ Sites LTE 4G transformés: {len(result)} sites")
    print(f"   Avec colonnes: {list(result.columns)}")
    return result


def transform_lte_cell_data(df, site_df_raw):
    """Transforme les données de cellule LTE 4G et les fusionne avec les sites."""
    print(f"🔍 Colonnes du fichier source (cellules LTE 4G): {list(df.columns)}")
    
    # Vérifier si DataFrame vide
    if len(df) == 0 or len(df.columns) == 0:
        raise ValueError(
            f"❌ Le fichier des cellules LTE est VIDE ou mal détecté!\n"
            f"   Colonnes trouvées: {list(df.columns)}"
        )
    
    df = df.copy()
    
    # Mappings flexibles pour les colonnes LTE 4G
    cell_name_col = find_matching_column(df, ['Cell Name', 'Cell_Name', 'cellule', 'cell'])
    cell_id_col = find_matching_column(df, ['Cell ID', 'Cell_ID', 'cell id', 'cellId', 'Local cell identity'])
    enodeb_name_col = find_matching_column(df, ['NE Name', 'ne name', 'eNodeB Name', 'enodeb name'])
    physical_cell_id_col = find_matching_column(df, ['Physical cell id', 'Physical_cell_id', 'pci', 'pci'])
    downlink_earfcn_col = find_matching_column(df, ['Downlink EARFCN', 'Downlink_EARFCN', 'downlink earfcn', 'downlink_earfcn'])
    
    print(f"Colonnes détectées: Cell Name={cell_name_col}, Cell ID={cell_id_col}, NE Name={enodeb_name_col}, PCI={physical_cell_id_col}, Downlink EARFCN={downlink_earfcn_col}")
    
    if not all([cell_name_col, cell_id_col, enodeb_name_col]):
        missing = []
        if not cell_name_col: missing.append("Cell Name")
        if not cell_id_col: missing.append("Cell ID")
        if not enodeb_name_col: missing.append("NE Name")
        
        raise ValueError(
            f"❌ Colonnes requises non trouvées pour LTE 4G!\n"
            f"   Colonnes manquantes: {', '.join(missing)}\n"
            f"   Colonnes trouvées: {list(df.columns)}"
        )
    
    # Sélectionner et renommer les colonnes
    df_selected = df[[cell_name_col, cell_id_col, enodeb_name_col]].copy()
    df_selected.columns = ['nom cellule', 'cellId', 'NE Name']
    
    # Ajouter Physical Cell ID si trouvée
    if physical_cell_id_col:
        df_selected['Physical Cell ID'] = df[physical_cell_id_col].values
    else:
        df_selected['Physical Cell ID'] = 'N/A'
    
    # Ajouter Downlink EARFCN si trouvée
    if downlink_earfcn_col:
        df_selected['Downlink EARFCN'] = df[downlink_earfcn_col].values
        print(f"   ✅ Colonne 'Downlink EARFCN' ajoutée")
    else:
        df_selected['Downlink EARFCN'] = 'N/A'
        print(f"   ⚠️  Colonne 'Downlink EARFCN' non trouvée")
    
    # Extraire le nom de ville du Cell Name (avant le tiret/underscore)
    df_selected['nom_ville'] = df_selected['nom cellule'].apply(extract_city_name_from_cell)
    print(f"❔ Noms de villes extraits des cellules: {df_selected['nom_ville'].unique()}")
    
    # Extraire le code site du NE Name
    df_selected['code site'] = df_selected['NE Name'].apply(lambda x: str(x).split('_')[0] if '_' in str(x) else str(x))
    print(f"❔ Codes sites extraits: {df_selected['code site'].unique()}")
    
    # Créer un mapping complet avec site names à partir des données brutes
    site_df_selected = site_df_raw.copy()
    
    # Trouver la colonne source pour le site ID dans les données brutes
    site_id_col = find_matching_column(site_df_selected, ['NE Name', 'ne name', 'eNodeB Name', 'enodeb name', 'MTN ID', 'code site'])
    
    if site_id_col:
        # Extraire le code site de la colonne source
        site_df_selected['code site'] = site_df_selected[site_id_col].astype(str).apply(lambda x: x.split('_')[0] if '_' in str(x) else x)
        # Créer le nom du site avec préfixe 4G_
        site_df_selected['nom site'] = '4G_' + site_df_selected['code site'].astype(str)
        site_mapping_full = site_df_selected[['code site', 'nom site']].drop_duplicates().copy()
    else:
        # Fallback: créer un mapping simplement à partir des codes extraits
        print(f"⚠️  Colonnes site non trouvées. Création du mapping depuis les cellules...")
        unique_codes = df_selected['code site'].unique()
        site_mapping_full = pd.DataFrame({
            'code site': unique_codes,
            'nom site': ['4G_' + str(code) for code in unique_codes]
        })
    
    print(f"\n📍 Mapping sites disponibles (LTE 4G):")
    print(f"   Code sites: {site_mapping_full['code site'].unique()}")
    
    # Fusion avec les sites
    print(f"\n🔗 Fusion par code site (LTE 4G)...")
    df_merged = df_selected.merge(
        site_mapping_full, 
        on='code site',
        how='left'
    )
    
    # Vérification 
    print(f"\n✅ VÉRIFICATION DES CORRESPONDANCES LTE 4G:")
    
    valid_cells = df_merged[df_merged['nom site'].notna()].copy()
    if len(valid_cells) > 0:
        print(f"\n📋 Cellules VALIDÉES ({len(valid_cells)}):")
        print(f"   Exemples de correspondances:")
        for idx, row in valid_cells.head(10).iterrows():
            print(f"   ✅ {row['nom cellule']:25s} → {row['nom site']:20s} (Code: {row['code site']})")
        
        df_merged = valid_cells.copy()
        print(f"\n✅ {len(df_merged)} cellules LTE 4G conservées après vérification")
    
    # Calculer l'azimuth basé sur la première lettre du suffixe pour 4G LTE
    df_merged['azimuth'] = df_merged['nom cellule'].apply(calculate_azimuth_lte)
    print(f"\n📐 Azimuth calculés LTE : {df_merged['azimuth'].value_counts().to_dict()}")
    
    # Colonnes finales (avec azimuth et Downlink EARFCN)
    cols = ['LTE_Cell', 'code site', 'nom cellule', 'cellId', 'Physical Cell ID', 'Downlink EARFCN', 'azimuth']
    df_merged['LTE_Cell'] = 'LTE_Cell'
    result = df_merged[cols].copy()
    
    # Trier par site puis par nom (cohérent avec 3G et 2G)
    result = result.sort_values(['code site', 'nom cellule']).reset_index(drop=True)
    
    print(f"\n✅ Transformation cellules LTE: {len(result)} lignes (triées par site)")
    return result

    
    # Supprimer les cellules orphelines (pas de matching)
    orphaned = df_selected[~df_selected.index.isin(df_merged.index)]
    if len(orphaned) > 0:
        print(f"\n⚠️  {len(orphaned)} cellules GSM ORPHELINES SUPPRIMÉES (pas de MTN Name correspondant):")
        for idx, row in orphaned.iterrows():
            print(f"   🗑️  {row['nom cellule']:20s} | Ville extraite: {row['nom_ville']}")
    
    # Ajouter la colonne GSM_Cell
    df_merged['GSM_Cell'] = 'GSM_Cell'
    
    # Calculer l'azimuth basé sur la dernière chiffre du nom de cellule
    df_merged['azimuth'] = df_merged['nom cellule'].apply(calculate_azimuth)
    print(f"\n📐 Azimuth calculés : {df_merged['azimuth'].value_counts().to_dict()}")
    
    # Colonnes finales (avec azimuth)
    cols = ['GSM_Cell', 'code site', 'nom cellule', 'cellId', 'BCCH Frequency', 'azimuth']
    result = df_merged[cols].copy()
    
    # Trier par site puis par nom (cohérent avec 3G)
    result = result.sort_values(['code site', 'nom cellule']).reset_index(drop=True)
    
    print(f"\n✅ Transformation cellules GSM: {len(result)} lignes (triées par site)")
    return result



