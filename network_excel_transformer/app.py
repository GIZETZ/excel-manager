# Network Excel Transformer - Streamlit App

import streamlit as st
import pandas as pd
import os
from modules.excel_reader import read_umts_source, read_database_template
from modules.transformer import transform_site_data, transform_cell_data, extract_code_site_from_nodeb_name
from modules.generator import generate_final_excel

st.set_page_config(page_title="Network Excel Transformer", layout="wide")

st.title("🔄 Network Excel Transformer")
st.markdown("Transformation automatique des fichiers Excel réseau (UMTS) pour remplir la base de données 2G/3G/4G")

# Créer deux colonnes pour les uploads
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Fichier Source")
    source_file = st.file_uploader("Importez UMTS CELL Info.xls", type=["xls", "xlsx"], key="source")

with col2:
    st.subheader("📦 Fichier de Base de Données")
    db_file = st.file_uploader("Importez 2G3G4G_Cell Info.xls", type=["xls", "xlsx"], key="db")

# Bouton de transformation
if st.button("🚀 Transformer les données", type="primary"):
    if source_file is None or db_file is None:
        st.error("❌ Veuillez importer les deux fichiers!")
    else:
        try:
            # Lire les fichiers
            st.info("📖 Lecture des fichiers...")
            sites_raw, cells_raw = read_umts_source(source_file)
            st.success(f"✅ Sites lus: {len(sites_raw)} lignes")
            st.success(f"✅ Cellules lues: {len(cells_raw)} lignes")
            
            # Afficher les colonnes pour debug
            with st.expander("🔍 Colonnes détectées"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Sites (Feuille 1):**")
                    st.write(list(sites_raw.columns))
                with col2:
                    st.write("**Cellules (Feuille 2):**")
                    st.write(list(cells_raw.columns))
            
            # Transformer les données
            st.info("⚙️ Transformation en cours...")
            sites_transformed = transform_site_data(sites_raw)
            st.success(f"✅ Sites transformés: {len(sites_transformed)} lignes")
            
            # Transformer les cellules avec les sites
            cells_raw_copy = cells_raw.copy()
            cells_transformed = transform_cell_data(cells_raw_copy, sites_raw)
            st.success(f"✅ Cellules transformées: {len(cells_transformed)} lignes")
            
            # Sauvegarder les fichiers temporaires
            temp_source = "temp_source.xlsx"
            temp_db = "temp_db.xlsx"
            source_file.seek(0)
            db_file.seek(0)
            with open(temp_source, "wb") as f:
                f.write(source_file.read())
            with open(temp_db, "wb") as f:
                f.write(db_file.read())
            
            # Générer le fichier Excel final
            st.info("📝 Génération du fichier final...")
            output_path = "output/2G3G4G_Cell Info_filled.xlsx"
            generate_final_excel(sites_transformed, cells_transformed, temp_db, output_path)
            st.success("✅ Fichier généré avec succès!")
            
            # Afficher les résultats
            st.success("✅ Transformation réussie!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Sites générés", len(sites_transformed))
            with col2:
                st.metric("✅ Cellules générées", len(cells_transformed))
            with col3:
                st.metric("📁 Fichier créé", "Prêt")
            
            # Afficher un aperçu des données
            st.subheader("📊 Aperçu des données générées")
            
            tab1, tab2 = st.tabs(["Sites (WCDMA_Site)", "Cellules (WCDMA_Cell)"])
            
            with tab1:
                st.dataframe(sites_transformed, use_container_width=True)
            
            with tab2:
                st.dataframe(cells_transformed, use_container_width=True)
            
            # Bouton de téléchargement
            st.subheader("📥 Téléchargement")
            with open(output_path, "rb") as file:
                st.download_button(
                    label="⬇️ Télécharger le fichier Excel",
                    data=file.read(),
                    file_name="2G3G4G_Cell Info_filled.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Nettoyage
            os.remove(temp_source)
            os.remove(temp_db)
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la transformation: {str(e)}")
            st.error(f"**Détails de l'erreur:**")
            import traceback
            st.code(traceback.format_exc())

