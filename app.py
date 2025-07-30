# app.py

import streamlit as st
import pandas as pd
import joblib
import numpy as np
import folium
from streamlit_folium import st_folium

# Charger le modèle entraîné
model = joblib.load("model_loyer.joblib")

st.set_page_config(page_title="Estimation Loyer Antananarivo", layout="wide")

st.title("🏠 Estimation du loyer à Antananarivo")

st.markdown("Remplissez les caractéristiques du logement pour estimer son loyer mensuel.")

# --- Interface utilisateur ---

col1, col2 = st.columns(2)

with col1:
    quartier = st.selectbox("Quartier", ['67Ha', 'Ambanidia', 'Ambatobe', 'Ambatonakanga', 'Ambatoroka', 'Ambodivona', 'Ambolokandrina', 'Ampandrana', 'Analakely', 'Analamahitsy', 'Andoharanofotsy', 'Andraharo', 'Ankadifotsy', 'Ankazobe', 'Anosibe', 'Isoraka', 'Ivandry', 'Soanierana', 'Tanjombato', 'Tsaralalana'])
    superficie = st.number_input("Superficie (m²)", min_value=10, max_value=500, value=50)
    nombre_chambres = st.number_input("Nombre de chambres", min_value=1, max_value=10, value=2)

with col2:
    douche_wc = st.selectbox("Douche/WC", ['interieur', 'exterieur'])
    type_d_acces = st.selectbox("Type d'accès", ['sans', 'moto', 'voiture', 'voiture_avec_par_parking'])
    meuble = st.selectbox("meuble", ['oui', 'non'])
    etat_general = st.selectbox("etat_general", ['bon', 'moyen', 'mauvais'])

# Créer le DataFrame d'entrée
input_data = pd.DataFrame({
    'quartier': [quartier],
    'superficie': [superficie],
    'nombre_chambres': [nombre_chambres],
    'douche_wc': [douche_wc],
    'type_d_acces': [type_d_acces],
    'meuble': [meuble],
    'etat_general': [etat_general]
})

# --- Prédiction ---
if st.button("📊 Prédire le loyer"):
    try:
        prediction = model.predict(input_data)[0]
        st.success(f"🏷️ Loyer estimé : {int(prediction):,} Ariary / mois")
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")

# --- Carte interactive ---
st.markdown("---")
st.subheader("🗺️ Localiser le logement sur la carte (optionnel)")

m = folium.Map(location=[-18.8792, 47.5079], zoom_start=13)
folium.Marker(location=[-18.8792, 47.5079], popup="Centre ville").add_to(m)

map_data = st_folium(m, width=700, height=500)

if map_data and map_data['last_clicked']:
    lat = map_data['last_clicked']['lat']
    lon = map_data['last_clicked']['lng']
    st.info(f"📍 Coordonnées sélectionnées : {lat:.5f}, {lon:.5f}")
    # À faire : associer coord. GPS à un quartier automatiquement (avec GeoJSON)

# --- Coefficients / Poids des variables ---
st.markdown("---")
if st.checkbox("📈 Afficher les poids des variables (coefs)"):
    try:
        model_lin = model.named_steps['regressor']
        features = model.named_steps['preprocessing'].get_feature_names_out()
        coefs = model_lin.coef_

        coef_df = pd.DataFrame({'Variable': features, 'Poids': coefs})
        coef_df = coef_df.sort_values(by='Poids', key=abs, ascending=False)

        st.dataframe(coef_df.style.background_gradient(cmap='Blues'))
    except Exception as e:
        st.warning(f"Impossible d'afficher les poids : {e}")
