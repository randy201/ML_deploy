import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
import math

# Charger le modèle
@st.cache_resource
def load_model():
    try:
        return joblib.load("model_loyer.joblib")
    except FileNotFoundError:
        st.error("⚠️ Modèle non trouvé. Assurez-vous que 'model_loyer.joblib' existe.")
        return None

model = load_model()

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

# Fonction pour calculer la distance
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en utilisant la formule de Haversine"""
    R = 6371  # Rayon de la Terre en km
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

# Fonction pour trouver le quartier le plus proche
def find_nearest_quartier(lat, lon, coords_dict):
    min_dist = float("inf")
    nearest_q = None
    for q, (q_lat, q_lon) in coords_dict.items():
        dist = calculate_distance(lat, lon, q_lat, q_lon)
        if dist < min_dist:
            min_dist = dist
            nearest_q = q
    return nearest_q, min_dist

# Fonction pour faire une prédiction
def make_prediction(quartier, superficie, nombre_chambres, douche_wc, type_d_acces, meuble, etat_general):
    if model is None:
        return None
    
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
        return int(prediction)
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
        return None

# Interface utilisateur
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Caractéristiques du logement")
    # Utiliser le quartier de session_state s'il existe, sinon la première option
    default_quartier = st.session_state.get('selected_quartier', list(quartier_coords.keys())[0])
    if default_quartier not in quartier_coords:
        default_quartier = list(quartier_coords.keys())[0]
    
    quartier_index = list(quartier_coords.keys()).index(default_quartier)
    quartier = st.selectbox("Quartier", list(quartier_coords.keys()), index=quartier_index, key="quartier_select")
    
    superficie = st.number_input("Superficie (m²)", min_value=10, max_value=500, value=50)
    nombre_chambres = st.number_input("Nombre de chambres", min_value=1, max_value=10, value=2)

with col2:
    st.write("")  # Espacement
    st.write("")
    douche_wc = st.selectbox("Douche/WC", ['interieur', 'exterieur'])
    type_d_acces = st.selectbox("Type d'accès", ['sans', 'moto', 'voiture', 'voiture_avec_par_parking'])
    meuble = st.selectbox("Meublé", ['oui', 'non'])
    etat_general = st.selectbox("État général", ['bon', 'moyen', 'mauvais'])

# Prédiction manuelle
if st.button("📊 Prédire le loyer", type="primary"):
    prediction = make_prediction(quartier, superficie, nombre_chambres, douche_wc, type_d_acces, meuble, etat_general)
    if prediction:
        st.success(f"🏷️ Loyer estimé pour **{quartier}** : **{prediction:,} Ariary / mois**")

# --- Carte interactive ---
st.markdown("---")
st.subheader("🗺️ Localisation interactive")
st.markdown("**Instructions :** Cliquez sur la carte pour sélectionner automatiquement le quartier le plus proche, ou cliquez sur un marqueur pour sélectionner directement ce quartier.")

# Initialiser l'état de session pour le quartier sélectionné
if 'selected_quartier' not in st.session_state:
    st.session_state.selected_quartier = None

# Créer la carte avec plus d'options
center_coords = [-18.8792, 47.5079]  # Centre d'Antananarivo
m = folium.Map(
    location=center_coords, 
    zoom_start=13,
    tiles='OpenStreetMap'
)

# Ajouter des marqueurs plus attractifs pour chaque quartier
for q, coords in quartier_coords.items():
    # Couleur différente si c'est le quartier sélectionné
    color = 'red' if q == quartier else 'blue'
    
    folium.Marker(
        location=coords, 
        popup=folium.Popup(f"<b>{q}</b><br>Cliquez pour sélectionner", max_width=200),
        tooltip=f"Quartier: {q}",
        icon=folium.Icon(color=color, icon='home', prefix='fa')
    ).add_to(m)

# Ajouter une légende
legend_html = '''
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 200px; height: 100px; 
     color: black;
     background-color: rgba(255, 255, 255, 0.5);
     backdrop-filter: blur(5px);
     border:2px solid grey; z-index:9999; 
     font-size:14px; padding: 10px">
<p><b>Légende</b></p>
<i class="fa fa-home" style="color:blue"></i> Quartiers disponibles<br>
<i class="fa fa-home" style="color:red"></i> Quartier sélectionné
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Disposer la carte et les contrôles côte à côte
col_map, col_controls = st.columns([2, 1])

with col_map:
    # Afficher la carte avec une clé unique pour forcer le rafraîchissement
    map_data = st_folium(
        m, 
        width=500, 
        height=500,
        returned_objects=["last_clicked", "last_object_clicked"],
        key=f"map_{quartier}"  # Clé dynamique pour rafraîchir la carte
    )

with col_controls:
    st.markdown("### 🎯 Contrôles de sélection")
    
    # Afficher les informations de clic ici
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        
        st.info(f"📍 **Position cliquée**\n📐 Lat: {lat:.5f}\n📐 Lon: {lon:.5f}")
        
        # Trouver le quartier le plus proche
        quartier_auto, distance = find_nearest_quartier(lat, lon, quartier_coords)
        
        if quartier_auto and distance < 5:  # Limite de 5km
            st.success(f"🎯 **Quartier détecté**\n📍 {quartier_auto}\n📏 Distance: {distance:.2f} km")
            
            # Bouton pour utiliser ce quartier - maintenant à côté de la carte
            if st.button(f"✅ Utiliser {quartier_auto}", key="use_auto_quartier", type="primary"):
                st.session_state.selected_quartier = quartier_auto
                st.rerun()
                
            # Prédiction automatique pour le quartier détecté
            st.markdown("---")
            st.markdown("### 🔮 Estimation automatique")
            
            prediction = make_prediction(quartier_auto, superficie, nombre_chambres, douche_wc, type_d_acces, meuble, etat_general)
            if prediction:
                st.metric(
                    label="💰 Loyer estimé",
                    value=f"{prediction:,} Ar/mois",
                    help=f"Estimation pour {quartier_auto}"
                )
                
                # Comparaison avec le quartier sélectionné manuellement
                if quartier_auto != quartier:
                    prediction_manual = make_prediction(quartier, superficie, nombre_chambres, douche_wc, type_d_acces, meuble, etat_general)
                    if prediction_manual:
                        diff = prediction - prediction_manual
                        diff_pct = (diff / prediction_manual) * 100
                        
                        st.metric(
                            label=f"📊 Vs {quartier}",
                            value=f"{diff:+,} Ar",
                            delta=f"{diff_pct:+.1f}%"
                        )
        else:
            st.warning("❌ **Aucun quartier proche**\n\nCliquez plus près d'un quartier (< 5km)")
    
    else:
        st.info("👆 **Cliquez sur la carte**\n\nPour détecter automatiquement le quartier le plus proche")
        
        # Afficher le quartier actuellement sélectionné
        st.markdown("---")
        st.markdown("### 📍 Quartier actuel")
        st.write(f"**{quartier}**")
        
        # Prédiction pour le quartier actuel
        prediction_current = make_prediction(quartier, superficie, nombre_chambres, douche_wc, type_d_acces, meuble, etat_general)
        if prediction_current:
            st.metric(
                label="💰 Loyer estimé",
                value=f"{prediction_current:,} Ar/mois"
            )

# Traitement des clics sur la carte
if map_data:
    # Si un marqueur a été cliqué
    if map_data.get("last_object_clicked") and map_data["last_object_clicked"].get("popup"):
        popup_text = map_data["last_object_clicked"]["popup"]
        # Extraire le nom du quartier du popup
        for q in quartier_coords.keys():
            if q in popup_text:
                st.session_state.selected_quartier = q
                st.rerun()

# Affichage d'informations supplémentaires
with st.expander("ℹ️ Informations sur l'application"):
    st.markdown("""
    **Comment utiliser cette application :**
    
    1. **Sélection manuelle** : Choisissez un quartier dans la liste déroulante et cliquez sur "Prédire le loyer"
    
    2. **Sélection par carte** :
       - **Cliquez sur un marqueur bleu** pour sélectionner directement ce quartier
       - **Cliquez n'importe où sur la carte** pour trouver automatiquement le quartier le plus proche
    
    3. **Comparaison** : L'application vous permet de comparer les prix entre différents quartiers
    
    **Données couvertes :** {len(quartier_coords)} quartiers d'Antananarivo
    """)

# Statistiques rapides sur les quartiers
if st.checkbox("📊 Afficher les statistiques des quartiers"):
    st.subheader("Aperçu des quartiers")
    
    # Créer un échantillon de prédictions pour chaque quartier (avec des valeurs standard)
    sample_predictions = []
    standard_params = {
        'superficie': 60,
        'nombre_chambres': 2, 
        'douche_wc': 'interieur',
        'type_d_acces': 'voiture',
        'meuble': 'non',
        'etat_general': 'bon'
    }
    
    if model:
        for q in quartier_coords.keys():
            pred = make_prediction(q, **standard_params)
            if pred:
                sample_predictions.append({'Quartier': q, 'Loyer_estimé': pred})
    
        if sample_predictions:
            df_stats = pd.DataFrame(sample_predictions)
            df_stats = df_stats.sort_values('Loyer_estimé', ascending=False)
            
            col_stats1, col_stats2 = st.columns(2)
            
            with col_stats1:
                st.markdown("**🏆 Top 5 - Quartiers les plus chers**")
                st.dataframe(df_stats.head(), hide_index=True)
            
            with col_stats2:
                st.markdown("**💰 Top 5 - Quartiers les moins chers**")
                st.dataframe(df_stats.tail(), hide_index=True)
            
            st.markdown(f"*Estimation basée sur : {standard_params['superficie']}m², {standard_params['nombre_chambres']} chambres, douche/WC intérieur, accès voiture, non meublé, bon état*")