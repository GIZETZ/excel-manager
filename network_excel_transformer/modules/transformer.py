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

def extract_city_name_from_cell(cell_name):
    """Extrait le nom de la ville du Cell Name (avant le tiret)."""
    if pd.isna(cell_name):
        return None
    cell_str = str(cell_name).strip()
    # Prend la partie avant le premier tiret
    if '-' in cell_str:
        return cell_str.split('-')[0].strip()
    return cell_str


def transform_cell_data(df, site_df_raw):
    """Transforme les données de cellule et les fusionne avec les sites par code ET nom de ville."""
    # Afficher les colonnes réelles pour debug
    print(f"🔍 Colonnes du fichier source (cellules): {list(df.columns)}")
    
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
    
    # Fusion 1: Par code site
    print(f"\n🔗 Fusion par CODE SITE...")
    df_merged = df_selected.merge(
        site_mapping[['code site', 'nom site']], 
        on='code site', 
        how='left'
    )
    
    # Fusion 2: Par nom de ville (pour les cellules orphelines - sans code site correspondant)
    print(f"🔗 Fusion par NOM DE VILLE...")
    orphaned = df_merged[df_merged['nom site'].isna()].copy()
    
    if len(orphaned) > 0:
        print(f"   ⚠️  {len(orphaned)} cellules orphelines détectées (pas de code site correspondant)")
        
        # Essayer de matcher par nom de ville
        orphaned_with_site = orphaned.merge(
            site_mapping[['nom_ville_site', 'nom site']].drop_duplicates(), 
            left_on='nom_ville_normalized', 
            right_on='nom_ville_site',
            how='left',
            suffixes=('', '_y')
        )
        
        # Remplacer les valeurs manquantes dans df_merged
        merged_indices = df_merged[df_merged['nom site'].isna()].index
        if len(merged_indices) > 0 and 'nom site_y' in orphaned_with_site.columns:
            df_merged.loc[merged_indices, 'nom site'] = orphaned_with_site['nom site_y'].values
        elif len(merged_indices) > 0 and 'nom site' in orphaned_with_site.columns:
            df_merged.loc[merged_indices, 'nom site'] = orphaned_with_site['nom site'].values
    
    # Supprimer les cellules orphelines restantes
    still_missing = df_merged[df_merged['nom site'].isna()]
    if len(still_missing) > 0:
        print(f"\n⚠️  {len(still_missing)} cellules ORPHELINES SUPPRIMÉES (pas de site correspondant):")
        for idx, row in still_missing.iterrows():
            print(f"   🗑️  Suppression: {row['nom cellule']} | Ville: {row['nom_ville']} | Code site: {row['code site']}")
        
        # Supprimer les cellules orphelines
        df_merged = df_merged[df_merged['nom site'].notna()].copy()
        print(f"\n✅ {len(df_merged)} cellules conservées après suppression des orphelines")
    else:
        print(f"\n✅ Toutes les cellules ({len(df_merged)}) ont un site correspondant!")
    
    # Ajouter la colonne WCDMA_Cell
    df_merged['WCDMA_Cell'] = 'WCDMA_Cell'
    
    # Colonnes nécessaires pour la feuille 3G (sans STATUT)
    cols = ['WCDMA_Cell', 'code site', 'nom cellule', 'cellId', 'Layer_type']
    result = df_merged[cols].copy()

    
    # 🔤 TRIER PAR NOM DE CELLULE (ORDRE ALPHABÉTIQUE)
    result = result.sort_values('nom cellule').reset_index(drop=True)
    
    print(f"✅ Transformation cellules: {len(result)} lignes (triées par nom)")
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
    
    print(f"Colonnes détectées: Cell Name={cell_name_col}, Cell ID={cell_id_col}, BTS Name={bts_name_col}, BCCH={bcch_freq_col}")
    
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
    df_selected = df[[cell_name_col, cell_id_col, bts_name_col]].copy()
    df_selected.columns = ['nom cellule', 'cellId', 'BTS Name']
    
    # Ajouter BCCH Frequency si trouvée
    if bcch_freq_col:
        df_selected['BCCH Frequency'] = df[[bcch_freq_col]]
    else:
        df_selected['BCCH Frequency'] = 'N/A'
    
    # Extraire le nom de ville du Cell Name (avant le tiret)
    df_selected['nom_ville'] = df_selected['nom cellule'].apply(extract_city_name_from_cell)
    print(f"❔ Noms de villes extraits des cellules: {df_selected['nom_ville'].unique()}")
    
    # Extraire le code site du BTS Name
    df_selected['code site'] = df_selected['BTS Name'].apply(extract_code_site_from_bts_name)
    print(f"❔ Codes sites extraits: {df_selected['code site'].unique()}")
    
    # Créer un mapping site
    site_mapping = site_df_raw[['MTN ID', 'MTN Name']].copy()
    site_mapping.columns = ['code site', 'MTN Name']
    site_mapping['nom_ville_site'] = site_mapping['MTN Name'].astype(str).str.strip().str.lower()
    site_mapping['nom site'] = '2G_' + site_mapping['MTN Name'].astype(str)
    print(f"\n📍 Mapping sites disponibles:")
    print(f"   Codes sites: {site_mapping['code site'].unique()}")
    
    # Normaliser les noms de villes
    df_selected['nom_ville_normalized'] = df_selected['nom_ville'].astype(str).str.strip().str.lower()
    
    # Fusion par code site
    print(f"\n🔗 Fusion par CODE SITE...")
    df_merged = df_selected.merge(
        site_mapping[['code site', 'nom site']], 
        on='code site', 
        how='left'
    )
    
    # Fusion par nom de ville pour les orphelines
    orphaned = df_merged[df_merged['nom site'].isna()].copy()
    if len(orphaned) > 0:
        print(f"   ⚠️  {len(orphaned)} cellules orphelines détectées")
        orphaned_with_site = orphaned.merge(
            site_mapping[['nom_ville_site', 'nom site']].drop_duplicates(), 
            left_on='nom_ville_normalized', 
            right_on='nom_ville_site',
            how='left',
            suffixes=('', '_y')
        )
        merged_indices = df_merged[df_merged['nom site'].isna()].index
        if len(merged_indices) > 0 and 'nom site_y' in orphaned_with_site.columns:
            df_merged.loc[merged_indices, 'nom site'] = orphaned_with_site['nom site_y'].values
    
    # Supprimer les cellules orphelines
    still_missing = df_merged[df_merged['nom site'].isna()]
    if len(still_missing) > 0:
        print(f"\n⚠️  {len(still_missing)} cellules GSM ORPHELINES SUPPRIMÉES:")
        df_merged = df_merged[df_merged['nom site'].notna()].copy()
        print(f"✅ {len(df_merged)} cellules GSM conservées")
    
    # Ajouter la colonne GSM_Cell
    df_merged['GSM_Cell'] = 'GSM_Cell'
    
    # Colonnes finales
    cols = ['GSM_Cell', 'code site', 'nom cellule', 'cellId', 'BCCH Frequency']
    result = df_merged[cols].copy()
    
    # Trier par nom
    result = result.sort_values('nom cellule').reset_index(drop=True)
    
    print(f"✅ Transformation cellules GSM: {len(result)} lignes (triées par nom)")
    return result



