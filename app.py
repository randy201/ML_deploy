import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
import math

# Charger le modèle
model = joblib.load("model_loyer.joblib")

st.set_page_config(page_title="Estimation Loyer Antananarivo", layout="wide")
st.title("🏠 Estimation du loyer à Antananarivo")
st.markdown("Remplissez les caractéristiques du logement pour estimer son loyer mensuel.")

# Coordonnées centrales par quartier
quartier_coords = {
    "67Ha": [-18.90914, 47.50751],
    "Ambatonakanga": [-18.91290, 47.52769],
    "Ambatoroka": [-18.92296, 47.54140],
    "Ambolokandrina": [-18.92180, 47.56042],
    "Ambodivona": [-18.89294, 47.52942],
    "Ampandrana": [-18.90417, 47.53303],
    "Analakely": [-18.90831, 47.52632],
    "Analamahitsy": [-18.87149, 47.54795],
    "Andoharanofotsy": [-18.98001, 47.53282],
    "Andraharo": [-18.88468, 47.50991],
    "Ankadifotsy": [-18.89792, 47.52559],
    "Ankazobe": [-18.31537, 47.11476],
    "Anosibe": [-18.92759, 47.51307],
    "Isoraka": [-18.91078, 47.52105],
    "Soanierana": [-18.93634, 47.52456],
    "Tanjombato": [-18.95869, 47.52791],
    "Tsaralalana": [-18.90745, 47.52111],
    "Ambanidia": [-18.90801, 47.52898],
    "Ambatobe": [-18.87621, 47.54958],
    "Ivandry": [-18.85827, 47.53220]
}

# Fonction pour trouver le quartier le plus proche
def find_nearest_quartier(lat, lon, coords_dict):
    min_dist = float("inf")
    nearest_q = None
    for q, (q_lat, q_lon) in coords_dict.items():
        dist = math.sqrt((lat - q_lat)**2 + (lon - q_lon)**2)
        if dist < min_dist:
            min_dist = dist
            nearest_q = q
    return nearest_q

# Interface utilisateur
col1, col2 = st.columns(2)

with col1:
    quartier = st.selectbox("Quartier", list(quartier_coords.keys()))
    superficie = st.number_input("Superficie (m²)", min_value=10, max_value=500, value=50)
    nombre_chambres = st.number_input("Nombre de chambres", min_value=1, max_value=10, value=2)

with col2:
    douche_wc = st.selectbox("Douche/WC", ['interieur', 'exterieur'])
    type_d_acces = st.selectbox("Type d'accès", ['sans', 'moto', 'voiture', 'voiture_avec_par_parking'])
    meuble = st.selectbox("Meublé", ['oui', 'non'])
    etat_general = st.selectbox("État général", ['bon', 'moyen', 'mauvais'])

# Prédiction manuelle
if st.button("📊 Prédire le loyer (manuel)"):
    input_data = pd.DataFrame({
        'quartier': [quartier],
        'superficie': [superficie],
        'nombre_chambres': [nombre_chambres],
        'douche_wc': [douche_wc],
        'type_d_acces': [type_d_acces],
        'meuble': [meuble],
        'etat_general': [etat_general]
    })
    try:
        prediction = model.predict(input_data)[0]
        st.success(f"🏷️ Loyer estimé : **{int(prediction):,} Ariary / mois**")
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")

# --- Carte interactive ---
st.markdown("---")
st.subheader("🗺️ Cliquez sur la carte pour localiser automatiquement le quartier")

# Créer la carte
m = folium.Map(location=[-18.8792, 47.5079], zoom_start=13)

# Ajouter les marqueurs des quartiers
for q, coords in quartier_coords.items():
    folium.Marker(location=coords, popup=q, icon=folium.Icon(color='orange', icon='map-marker', prefix='fa')).add_to(m)

# Afficher la carte
map_data = st_folium(m, width=700, height=500)

# Si un point a été cliqué
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.info(f"📍 Coordonnées sélectionnées : {lat:.5f}, {lon:.5f}")

    quartier_auto = find_nearest_quartier(lat, lon, quartier_coords)
    if quartier_auto:
        st.success(f"Quartier détecté automatiquement : **{quartier_auto}**")

        input_data = pd.DataFrame({
            'quartier': [quartier_auto],
            'superficie': [superficie],
            'nombre_chambres': [nombre_chambres],
            'douche_wc': [douche_wc],
            'type_d_acces': [type_d_acces],
            'meuble': [meuble],
            'etat_general': [etat_general]
        })

        try:
            prediction = model.predict(input_data)[0]
            st.success(f"🔮 Loyer estimé pour {quartier_auto} : **{int(prediction):,} Ariary / mois**")
        except Exception as e:
            st.error(f"Erreur de prédiction : {e}")
    else:
        st.warning("❌ Aucun quartier détecté à proximité.")
