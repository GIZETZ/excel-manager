# Network Excel Transformer - Streamlit App

import streamlit as st
import pandas as pd
import os
import zipfile
import io
from modules.excel_reader import read_umts_source, read_gsm_source
from modules.transformer import transform_site_data, transform_cell_data, transform_gsm_cell_data
from modules.generator import generate_final_excel, generate_gsm_excel

st.set_page_config(page_title="Network Excel Transformer", layout="wide")

st.title("🔄 Network Excel Transformer")
st.markdown("Transformation automatique des fichiers Excel réseau (2G GSM / 3G UMTS)")

# Créer les onglets pour 3G et 2G
tab_3g, tab_2g = st.tabs(["🌐 3G UMTS", "📱 2G GSM"])

# ==================== ONGLET 3G ====================
with tab_3g:
    st.subheader("3G UMTS - Transformation")
    
    # Upload du fichier source 3G
    st.markdown("**📤 Fichier Source 3G**")
    source_file_3g = st.file_uploader("Importez UMTS CELL Info.xls avec SITES et CELLULES 3G", 
                                      type=["xls", "xlsx"], key="source_3g")
    
    # Bouton de transformation 3G
    if st.button("🚀 Transformer 3G", type="primary", key="btn_transform_3g"):
        if source_file_3g is None:
            st.error("❌ Veuillez importer le fichier source 3G!")
        else:
            try:
                # Lire les fichiers
                st.info("📖 Lecture des fichiers 3G...")
                sites_raw, cells_raw = read_umts_source(source_file_3g)
                st.success(f"✅ Sites 3G lus: {len(sites_raw)} lignes")
                st.success(f"✅ Cellules 3G lues: {len(cells_raw)} lignes")
                
                # Afficher les colonnes pour debug
                with st.expander("🔍 Colonnes détectées 3G"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Sites:**")
                        st.write(list(sites_raw.columns))
                    with col2:
                        st.write("**Cellules:**")
                        st.write(list(cells_raw.columns))
                
                # Transformer les données
                st.info("⚙️ Transformation 3G en cours...")
                sites_transformed = transform_site_data(sites_raw)
                st.success(f"✅ Sites 3G transformés: {len(sites_transformed)} lignes")
                
                cells_raw_copy = cells_raw.copy()
                cells_transformed = transform_cell_data(cells_raw_copy, sites_raw)
                st.success(f"✅ Cellules 3G transformées: {len(cells_transformed)} lignes")
                
                # Générer les deux fichiers Excel finaux
                st.info("📝 Génération des fichiers 3G...")
                output_path_sites_3g = "output/2G3G4G_Cell Info_SITES_3G.xlsx"
                output_path_cells_3g = "output/2G3G4G_Cell Info_CELLS_3G.xlsx"
                generate_final_excel(sites_transformed, cells_transformed, output_path_sites_3g, output_path_cells_3g)
                st.success("✅ Fichiers 3G générés avec succès!")
                
                # Métriques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Sites 3G générés", len(sites_transformed))
                with col2:
                    st.metric("✅ Cellules 3G générées", len(cells_transformed))
                with col3:
                    st.metric("📁 Fichiers créés", "2 fichiers")
                
                # Aperçu des données
                st.subheader("📊 Aperçu des données 3G générées")
                
                tab1, tab2 = st.tabs(["Sites (WCDMA_Site)", "Cellules (WCDMA_Cell)"])
                
                with tab1:
                    st.dataframe(sites_transformed, use_container_width=True)
                
                with tab2:
                    st.dataframe(cells_transformed, use_container_width=True)
                
                # Téléchargement
                st.subheader("📥 Téléchargement 3G")
                
                st.markdown("**📦 Télécharger les 2 fichiers 3G ensemble :**")
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.write(output_path_sites_3g, arcname="2G3G4G_Cell Info_SITES_3G.xlsx")
                    zip_file.write(output_path_cells_3g, arcname="2G3G4G_Cell Info_CELLS_3G.xlsx")
                
                zip_buffer.seek(0)
                st.download_button(
                    label="⬇️ Télécharger 3G (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="2G3G4G_Cell_Info_3G.zip",
                    mime="application/zip",
                    key="zip_3g"
                )
                
                st.divider()
                
                st.markdown("**📄 Ou télécharger individuellement :**")
                col1, col2 = st.columns(2)
                
                with col1:
                    with open(output_path_sites_3g, "rb") as file:
                        st.download_button(
                            label="⬇️ Télécharger SITES 3G",
                            data=file.read(),
                            file_name="2G3G4G_Cell Info_SITES_3G.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="sites_btn_3g"
                        )
                
                with col2:
                    with open(output_path_cells_3g, "rb") as file:
                        st.download_button(
                            label="⬇️ Télécharger CELLULES 3G",
                            data=file.read(),
                            file_name="2G3G4G_Cell Info_CELLS_3G.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="cells_btn_3g"
                        )
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la transformation 3G: {str(e)}")
                st.error(f"**Détails de l'erreur:**")
                import traceback
                st.code(traceback.format_exc())


# ==================== ONGLET 2G ====================
with tab_2g:
    st.subheader("2G GSM - Transformation")
    
    # Upload du fichier source 2G
    st.markdown("**📤 Fichier Source 2G**")
    source_file_2g = st.file_uploader("Importez GSM CELL Info.xls avec SITES et CELLULES 2G", 
                                      type=["xls", "xlsx"], key="source_2g")
    
    # Bouton de transformation 2G
    if st.button("🚀 Transformer 2G", type="primary", key="btn_transform_2g"):
        if source_file_2g is None:
            st.error("❌ Veuillez importer le fichier source 2G!")
        else:
            try:
                # Lire les fichiers
                st.info("📖 Lecture des fichiers 2G...")
                sites_raw, cells_raw = read_gsm_source(source_file_2g)
                st.success(f"✅ Sites 2G lus: {len(sites_raw)} lignes")
                st.success(f"✅ Cellules 2G lues: {len(cells_raw)} lignes")
                
                # Afficher les colonnes pour debug
                with st.expander("🔍 Colonnes détectées 2G"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Sites:**")
                        st.write(list(sites_raw.columns))
                    with col2:
                        st.write("**Cellules:**")
                        st.write(list(cells_raw.columns))
                
                # Transformer les données
                st.info("⚙️ Transformation 2G en cours...")
                sites_transformed = transform_site_data(sites_raw)
                st.success(f"✅ Sites 2G transformés: {len(sites_transformed)} lignes")
                
                cells_raw_copy = cells_raw.copy()
                cells_transformed = transform_gsm_cell_data(cells_raw_copy, sites_raw)
                st.success(f"✅ Cellules 2G transformées: {len(cells_transformed)} lignes")
                
                # Générer les deux fichiers Excel finaux
                st.info("📝 Génération des fichiers 2G...")
                output_path_sites_2g = "output/2G3G4G_Cell Info_SITES_2G.xlsx"
                output_path_cells_2g = "output/2G3G4G_Cell Info_CELLS_2G.xlsx"
                generate_gsm_excel(sites_transformed, cells_transformed, output_path_sites_2g, output_path_cells_2g)
                st.success("✅ Fichiers 2G générés avec succès!")
                
                # Métriques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Sites 2G générés", len(sites_transformed))
                with col2:
                    st.metric("✅ Cellules 2G générées", len(cells_transformed))
                with col3:
                    st.metric("📁 Fichiers créés", "2 fichiers")
                
                # Aperçu des données
                st.subheader("📊 Aperçu des données 2G générées")
                
                tab1, tab2 = st.tabs(["Sites (GSM_Site)", "Cellules (GSM_Cell)"])
                
                with tab1:
                    st.dataframe(sites_transformed, use_container_width=True)
                
                with tab2:
                    st.dataframe(cells_transformed, use_container_width=True)
                
                # Téléchargement
                st.subheader("📥 Téléchargement 2G")
                
                st.markdown("**📦 Télécharger les 2 fichiers 2G ensemble :**")
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.write(output_path_sites_2g, arcname="2G3G4G_Cell Info_SITES_2G.xlsx")
                    zip_file.write(output_path_cells_2g, arcname="2G3G4G_Cell Info_CELLS_2G.xlsx")
                
                zip_buffer.seek(0)
                st.download_button(
                    label="⬇️ Télécharger 2G (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="2G3G4G_Cell_Info_2G.zip",
                    mime="application/zip",
                    key="zip_2g"
                )
                
                st.divider()
                
                st.markdown("**📄 Ou télécharger individuellement :**")
                col1, col2 = st.columns(2)
                
                with col1:
                    with open(output_path_sites_2g, "rb") as file:
                        st.download_button(
                            label="⬇️ Télécharger SITES 2G",
                            data=file.read(),
                            file_name="2G3G4G_Cell Info_SITES_2G.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="sites_btn_2g"
                        )
                
                with col2:
                    with open(output_path_cells_2g, "rb") as file:
                        st.download_button(
                            label="⬇️ Télécharger CELLULES 2G",
                            data=file.read(),
                            file_name="2G3G4G_Cell Info_CELLS_2G.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="cells_btn_2g"
                        )
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la transformation 2G: {str(e)}")
                st.error(f"**Détails de l'erreur:**")
                import traceback
                st.code(traceback.format_exc())

