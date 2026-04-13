# Network Excel Transformer - Streamlit App

import streamlit as st
import pandas as pd
import os
import zipfile
import io
from modules.excel_reader import read_umts_source
from modules.transformer import transform_site_data, transform_cell_data
from modules.generator import generate_final_excel

st.set_page_config(page_title="Network Excel Transformer", layout="wide")

st.title("🔄 Network Excel Transformer")
st.markdown("Transformation automatique du fichier Excel réseau (UMTS) vers les fichiers 2G/3G/4G")

# Upload du fichier source
st.subheader("📤 Fichier Source")
source_file = st.file_uploader("Importez UMTS CELL Info.xls avec SITES et CELLULES", type=["xls", "xlsx"], key="source")

# Bouton de transformation
if st.button("🚀 Transformer les données", type="primary"):
    if source_file is None:
        st.error("❌ Veuillez importer le fichier source!")
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
            
            # Générer les deux fichiers Excel finaux (SITES et CELLULES)
            st.info("📝 Génération des fichiers finaux...")
            output_path_sites = "output/2G3G4G_Cell Info_filled_SITES.xlsx"
            output_path_cells = "output/2G3G4G_Cell Info_filled_CELLS.xlsx"
            generate_final_excel(sites_transformed, cells_transformed, output_path_sites, output_path_cells)
            st.success("✅ Fichiers générés avec succès!")
            
            # Afficher les résultats
            st.success("✅ Transformation réussie!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Sites générés", len(sites_transformed))
            with col2:
                st.metric("✅ Cellules générées", len(cells_transformed))
            with col3:
                st.metric("📁 Fichiers créés", "2 fichiers")
            
            # Afficher un aperçu des données
            st.subheader("📊 Aperçu des données générées")
            
            tab1, tab2 = st.tabs(["Sites (WCDMA_Site)", "Cellules (WCDMA_Cell)"])
            
            with tab1:
                st.dataframe(sites_transformed, use_container_width=True)
            
            with tab2:
                st.dataframe(cells_transformed, use_container_width=True)
            
            # Boutons de téléchargement pour les deux fichiers
            st.subheader("📥 Téléchargement")
            
            # Créer un bouton pour télécharger les deux fichiers zippés
            st.markdown("**📦 Télécharger les 2 fichiers ensemble :**")
            
            # Créer le ZIP en mémoire
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Ajouter les deux fichiers au ZIP
                zip_file.write(output_path_sites, arcname="2G3G4G_Cell Info_SITES.xlsx")
                zip_file.write(output_path_cells, arcname="2G3G4G_Cell Info_CELLS.xlsx")
            
            zip_buffer.seek(0)
            st.download_button(
                label="⬇️ Télécharger TOUS LES FICHIERS (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="2G3G4G_Cell_Info_All.zip",
                mime="application/zip"
            )
            
            # Séparation
            st.divider()
            
            # Téléchargement individuel
            st.markdown("**📄 Ou télécharger individuellement :**")
            col1, col2 = st.columns(2)
            
            with col1:
                with open(output_path_sites, "rb") as file:
                    st.download_button(
                        label="⬇️ Télécharger SITES",
                        data=file.read(),
                        file_name="2G3G4G_Cell Info_SITES.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="sites_btn"
                    )
            
            with col2:
                with open(output_path_cells, "rb") as file:
                    st.download_button(
                        label="⬇️ Télécharger CELLULES",
                        data=file.read(),
                        file_name="2G3G4G_Cell Info_CELLS.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="cells_btn"
                    )

            

            
        except Exception as e:
            st.error(f"❌ Erreur lors de la transformation: {str(e)}")
            st.error(f"**Détails de l'erreur:**")
            import traceback
            st.code(traceback.format_exc())

