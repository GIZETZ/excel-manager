# Module: transformer.py

import pandas as pd
import re

def find_matching_column(df, possible_names):
    """Trouve une colonne dans le DataFrame en testant plusieurs noms possibles."""
    for col in df.columns:
        if col.strip() in possible_names:
            return col
        if col.strip().lower() in [name.lower() for name in possible_names]:
            return col
    return None

def transform_site_data(df):
    """Transforme les données de site selon les correspondances UMTS vers DB."""
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

def extract_code_site_from_nodeb_name(nodeb_name):
    """Extrait le code site du nom NodeB (ex: 3G_CI00001_Abengourou1 -> CI00001)."""
    if pd.isna(nodeb_name):
        return None
    match = re.search(r'CI\d{5}', str(nodeb_name))
    if match:
        return match.group()
    return None

def transform_cell_data(df, site_df_raw):
    """Transforme les données de cellule et les fusionne avec les sites."""
    # Afficher les colonnes réelles pour debug
    print(f"🔍 Colonnes du fichier source (cellules): {list(df.columns)}")
    df = df.copy()
    
    # Mappings flexibles pour chaque colonne
    cell_name_col = find_matching_column(df, ['Cell Name', 'Cell_Name', 'cellule', 'cell'])
    dl_prim_col = find_matching_column(df, ['DL Primary Scrambling Code', 'DL_Primary_Scrambling_Code', 'cellId', 'code'])
    downlink_col = find_matching_column(df, ['Downlink UARFCN', 'Downlink_UARFCN', 'Layer_type', 'layer'])
    nodeb_col = find_matching_column(df, ['NodeB Name', 'NodeB_Name', 'nodeb', 'name'])
    
    print(f"Colonnes détectées: Cell Name={cell_name_col}, DL Prim={dl_prim_col}, Downlink={downlink_col}, NodeB={nodeb_col}")
    
    if not all([cell_name_col, dl_prim_col, downlink_col, nodeb_col]):
        raise ValueError(f"Colonnes requises non trouvées. Colonne NodeB requise: {nodeb_col}. Présentes: {list(df.columns)}")
    
    # Sélectionner et renommer les colonnes nécessaires
    df_selected = df[[cell_name_col, dl_prim_col, downlink_col, nodeb_col]].copy()
    df_selected.columns = ['nom cellule', 'cellId', 'Layer_type', 'NodeB Name']
    
    # Extraire le code site du NodeB Name
    df_selected['code site'] = df_selected['NodeB Name'].apply(extract_code_site_from_nodeb_name)
    
    print(f"Codes sites extraits: {df_selected['code site'].unique()}")
    
    # Fusionner avec les données site brutes pour récupérer nom site
    site_mapping = site_df_raw[['MTN ID', 'MTN Name']].copy()
    site_mapping.columns = ['code site', 'nom site_original']
    site_mapping['nom site'] = '3G_' + site_mapping['nom site_original'].astype(str)
    site_mapping = site_mapping[['code site', 'nom site']].drop_duplicates()
    
    df_selected = df_selected.merge(site_mapping, on='code site', how='left')
    
    print(f"Fusion sites-cellules: {len(df_selected)} cellules fusionnées")
    
    # Ajouter la colonne WCDMA_Cell
    df_selected['WCDMA_Cell'] = 'WCDMA_Cell'
    
    # Colonnes nécessaires pour la feuille 3G
    cols = ['WCDMA_Cell', 'code site', 'nom cellule', 'cellId', 'Layer_type']
    result = df_selected[cols].copy()
    
    # 🔤 TRIER PAR NOM DE CELLULE (ORDRE ALPHABÉTIQUE)
    result = result.sort_values('nom cellule').reset_index(drop=True)
    
    print(f"✅ Transformation cellules: {len(result)} lignes (triées par nom)")
    return result


