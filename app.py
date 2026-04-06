# =============================================================================
# FoodTrace — Système de Traçabilité Alimentaire Big Data + Blockchain
# Projet : Cours Big Data — ENSIT 2ème année Génie Industriel
# Auteur  : Étudiant GI2 — Clarke Energy / ENSIT
# =============================================================================

import streamlit as st
import fakeredis
import hashlib
import json
import time
import random
import math
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Optional

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION STREAMLIT (doit être la première commande Streamlit)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FoodTrace — Supply Chain Intelligence",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLES CSS PERSONNALISÉS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* === IMPORTS GOOGLE FONTS === */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* === VARIABLES DE COULEUR === */
:root {
    --vert-data: #00FF9C;
    --bleu-chain: #00C2FF;
    --rouge-alerte: #FF3B3B;
    --orange-warn: #FF8C00;
    --fond-sombre: #0A0E1A;
    --fond-carte: #111827;
    --fond-carte2: #1C2333;
    --texte-principal: #E8EDF5;
    --texte-secondaire: #8899BB;
    --bordure: #2A3550;
}

/* === FOND GLOBAL === */
.stApp {
    background-color: var(--fond-sombre);
    font-family: 'Syne', sans-serif;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1321 0%, #111827 100%);
    border-right: 1px solid var(--bordure);
}

/* === TITRES === */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: var(--texte-principal) !important;
}

/* === MÉTRIQUES === */
[data-testid="metric-container"] {
    background: var(--fond-carte);
    border: 1px solid var(--bordure);
    border-radius: 12px;
    padding: 16px;
}

/* === CARTE BLOC BLOCKCHAIN === */
.bloc-card {
    background: var(--fond-carte2);
    border: 1px solid var(--bordure);
    border-left: 4px solid var(--bleu-chain);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: var(--texte-secondaire);
    transition: all 0.3s ease;
}

.bloc-card:hover {
    border-left-color: var(--vert-data);
    background: #1f2d47;
}

.bloc-card .bloc-index {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 800;
    color: var(--bleu-chain);
    margin-bottom: 8px;
}

.bloc-card .bloc-hash {
    color: var(--vert-data);
    word-break: break-all;
    font-size: 11px;
}

.bloc-card .bloc-prev {
    color: var(--orange-warn);
    word-break: break-all;
    font-size: 11px;
}

/* === ALERTE FRAUDE === */
.alerte-fraude {
    background: linear-gradient(135deg, #2D0A0A 0%, #1A0505 100%);
    border: 2px solid var(--rouge-alerte);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    animation: pulse-rouge 1.5s infinite;
}

@keyframes pulse-rouge {
    0%   { box-shadow: 0 0 0 0 rgba(255,59,59,0.4); }
    70%  { box-shadow: 0 0 0 15px rgba(255,59,59,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,59,59,0); }
}

.alerte-titre {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: var(--rouge-alerte);
    margin-bottom: 8px;
}

.alerte-details {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: #FF8888;
    margin-top: 12px;
}

/* === BADGE OK === */
.badge-ok {
    background: linear-gradient(135deg, #052D1C 0%, #0A1F14 100%);
    border: 2px solid var(--vert-data);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.badge-ok-titre {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--vert-data);
}

/* === TAGS ACTEURS === */
.acteur-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    margin: 4px;
}

/* === HEADER TITRE === */
.app-header {
    background: linear-gradient(135deg, #0D1321 0%, #1a2744 100%);
    border: 1px solid var(--bordure);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

.app-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 60%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(0,194,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}

.app-title {
    font-family: 'Syne', sans-serif;
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(90deg, #00C2FF, #00FF9C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

.app-subtitle {
    color: var(--texte-secondaire);
    font-size: 14px;
    margin-top: 6px;
}

/* === SÉPARATEUR === */
.section-sep {
    border: none;
    border-top: 1px solid var(--bordure);
    margin: 20px 0;
}

/* === TABLEAU DONNÉES === */
.dataframe {
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
}

/* === BOUTONS === */
.stButton button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

/* === ONGLETS === */
.stTabs [data-baseweb="tab-list"] {
    background: var(--fond-carte);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    color: var(--texte-secondaire) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}

.stTabs [aria-selected="true"] {
    background: var(--fond-carte2) !important;
    color: var(--texte-principal) !important;
}

/* === SELECTBOX / SLIDER === */
.stSelectbox, .stSlider {
    color: var(--texte-principal) !important;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SECTION 1 — CLASSE BLOCKCHAIN
# Implémentation d'une blockchain simple avec SHA-256 et Proof of Work
# =============================================================================

@dataclass
class Bloc:
    """Représente un bloc dans la chaîne."""
    index: int
    timestamp: str
    lot_id: str
    acteur: str
    donnees_hash: str          # Hash du lot de données Big Data
    hash_precedent: str
    nonce: int = 0
    hash_bloc: str = ""

    def calculer_hash(self) -> str:
        """Calcule le hash SHA-256 de ce bloc."""
        contenu = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "lot_id": self.lot_id,
            "acteur": self.acteur,
            "donnees_hash": self.donnees_hash,
            "hash_precedent": self.hash_precedent,
            "nonce": self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(contenu.encode()).hexdigest()

    def miner(self, difficulte: int = 3):
        """Proof of Work simplifié : trouver un nonce tel que le hash commence par N zéros."""
        cible = "0" * difficulte
        while not self.hash_bloc.startswith(cible):
            self.nonce += 1
            self.hash_bloc = self.calculer_hash()


class Blockchain:
    """Chaîne de blocs pour sceller les lots de données alimentaires."""

    DIFFICULTE = 3  # Proof of Work : le hash doit commencer par 3 zéros

    def __init__(self):
        self.chaine: List[Bloc] = []
        self._creer_bloc_genese()

    def _creer_bloc_genese(self):
        """Crée le tout premier bloc (bloc zéro) de la chaîne."""
        genese = Bloc(
            index=0,
            timestamp=datetime.now().isoformat(),
            lot_id="GENESE",
            acteur="SYSTEME",
            donnees_hash="0" * 64,
            hash_precedent="0" * 64,
        )
        genese.miner(self.DIFFICULTE)
        self.chaine.append(genese)

    def ajouter_bloc(self, lot_id: str, acteur: str, donnees_hash: str) -> Bloc:
        """Mine et ajoute un nouveau bloc à la chaîne."""
        bloc = Bloc(
            index=len(self.chaine),
            timestamp=datetime.now().isoformat(),
            lot_id=lot_id,
            acteur=acteur,
            donnees_hash=donnees_hash,
            hash_precedent=self.chaine[-1].hash_bloc,
        )
        bloc.miner(self.DIFFICULTE)
        self.chaine.append(bloc)
        return bloc

    def verifier_integrite(self) -> tuple[bool, str]:
        """
        Vérifie que la chaîne n'a pas été altérée.
        Retourne (True, message_ok) ou (False, message_erreur).
        """
        for i in range(1, len(self.chaine)):
            bloc_actuel = self.chaine[i]
            bloc_precedent = self.chaine[i - 1]

            # Vérification du hash du bloc actuel
            if bloc_actuel.hash_bloc != bloc_actuel.calculer_hash():
                return False, f"Bloc #{i} : hash invalide (données corrompues)"

            # Vérification du lien avec le bloc précédent
            if bloc_actuel.hash_precedent != bloc_precedent.hash_bloc:
                return False, f"Bloc #{i} : lien brisé avec le bloc #{i-1}"

        return True, "Chaîne intègre — Aucune falsification détectée"

    def hash_donnees(self, donnees: list) -> str:
        """Calcule le hash SHA-256 d'un lot de données IoT."""
        payload = json.dumps(donnees, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()


# =============================================================================
# SECTION 2 — SIMULATEUR IoT (Données Big Data)
# Génère un flux de données temps réel : Température, Humidité, GPS
# =============================================================================

ACTEURS = {
    "🌾 Producteur": {"couleur": "#00FF9C", "ville": "Tunis", "lat": 36.8065, "lon": 10.1815},
    "🚚 Transporteur": {"couleur": "#00C2FF", "ville": "Zaghouan", "lat": 36.4014, "lon": 10.1433},
    "🏭 Grossiste": {"couleur": "#FF8C00", "ville": "Sousse", "lat": 35.8256, "lon": 10.6369},
    "🏪 Détaillant": {"couleur": "#B06EFF", "ville": "Sfax", "lat": 34.7398, "lon": 10.7600},
}

# Seuils de température pour la viande fraîche (norme HACCP)
TEMP_MIN = 0.0   # °C
TEMP_MAX = 4.0   # °C
HUMID_MIN = 85   # %
HUMID_MAX = 95   # %


def generer_mesure(acteur: str, lot_id: str, avec_anomalie: bool = False) -> dict:
    """Génère une mesure IoT simulée pour un acteur donné."""
    info = ACTEURS[acteur]
    ts = datetime.now()

    # Simulation d'un léger bruit sinusoïdal autour de 2°C (comportement réaliste)
    bruit = math.sin(ts.second / 10) * 0.3
    temp_base = 2.0 + bruit + random.uniform(-0.5, 0.5)

    if avec_anomalie:
        # Anomalie : rupture de la chaîne du froid
        temp_base += random.uniform(6, 14)

    return {
        "lot_id": lot_id,
        "acteur": acteur,
        "timestamp": ts.isoformat(),
        "temperature": round(temp_base, 2),
        "humidite": round(random.uniform(HUMID_MIN, HUMID_MAX), 1),
        "gps_lat": round(info["lat"] + random.uniform(-0.01, 0.01), 6),
        "gps_lon": round(info["lon"] + random.uniform(-0.01, 0.01), 6),
        "ville": info["ville"],
        "conforme": TEMP_MIN <= temp_base <= TEMP_MAX,
    }


# =============================================================================
# SECTION 3 — INITIALISATION DE L'ÉTAT (Session State Streamlit)
# Remplace Redis pour la démo (fakeredis en mémoire)
# =============================================================================

def initialiser_etat():
    """Initialise toutes les variables de session au démarrage."""

    if "blockchain" not in st.session_state:
        st.session_state.blockchain = Blockchain()

    if "redis_client" not in st.session_state:
        # fakeredis simule un serveur Redis en mémoire — concept NoSQL vu en cours
        st.session_state.redis_client = fakeredis.FakeRedis(decode_responses=True)

    if "historique_mesures" not in st.session_state:
        st.session_state.historique_mesures = []  # Buffer Big Data en mémoire

    if "lots" not in st.session_state:
        st.session_state.lots = {}  # {lot_id: [mesures]}

    if "lot_actif" not in st.session_state:
        st.session_state.lot_actif = "LOT-2025-001"

    if "simulation_active" not in st.session_state:
        st.session_state.simulation_active = False

    if "compteur_mesures" not in st.session_state:
        st.session_state.compteur_mesures = 0

    if "fraude_detectee" not in st.session_state:
        st.session_state.fraude_detectee = False

    if "detail_fraude" not in st.session_state:
        st.session_state.detail_fraude = {}

    if "anomalie_active" not in st.session_state:
        st.session_state.anomalie_active = False


def ingerer_mesure(acteur: str, lot_id: str):
    """
    Ingestion d'une mesure IoT dans Redis (modèle BASE) et mise à jour du buffer Big Data.
    Tous les 10 messages → minage d'un nouveau bloc Blockchain.
    """
    r = st.session_state.redis_client
    bc = st.session_state.blockchain

    # Génération de la mesure avec éventuelle anomalie
    anomalie = st.session_state.anomalie_active and random.random() < 0.3
    mesure = generer_mesure(acteur, lot_id, avec_anomalie=anomalie)

    # ── Stockage NoSQL Redis (modèle BASE : disponibilité > cohérence stricte) ──
    cle = f"lot:{lot_id}:mesures"
    r.rpush(cle, json.dumps(mesure))      # Liste Redis pour le flux temps réel
    r.set(f"lot:{lot_id}:derniere", json.dumps(mesure))  # Hash Redis — accès O(1)
    r.incr(f"lot:{lot_id}:compteur")

    # ── Mise à jour du buffer historique ──
    st.session_state.historique_mesures.append(mesure)
    st.session_state.compteur_mesures += 1

    if lot_id not in st.session_state.lots:
        st.session_state.lots[lot_id] = []
    st.session_state.lots[lot_id].append(mesure)

    # ── Scellement Blockchain toutes les 10 mesures ──
    buffer = st.session_state.lots[lot_id]
    if len(buffer) % 10 == 0 and len(buffer) > 0:
        lot_data = buffer[-10:]  # Les 10 dernières mesures
        donnees_hash = bc.hash_donnees(lot_data)
        bc.ajouter_bloc(
            lot_id=lot_id,
            acteur=acteur,
            donnees_hash=donnees_hash
        )

    return mesure


# =============================================================================
# SECTION 4 — SIDEBAR
# =============================================================================

def afficher_sidebar():
    """Affiche le panneau latéral de contrôle."""
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 16px 0;'>
            <div style='font-family:Syne,sans-serif; font-size:22px; font-weight:800;
                        background:linear-gradient(90deg,#00C2FF,#00FF9C);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        background-clip:text;'>
                🔗 FoodTrace
            </div>
            <div style='color:#8899BB; font-size:11px; margin-top:4px;'>
                Big Data × Blockchain — ENSIT GI2
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Sélection du lot ──
        st.markdown("**📦 Lot actif**")
        lot_id = st.selectbox(
            "Identifiant du lot",
            ["LOT-2025-001", "LOT-2025-002", "LOT-2025-003"],
            label_visibility="collapsed"
        )
        st.session_state.lot_actif = lot_id

        st.divider()

        # ── Contrôles simulation ──
        st.markdown("**⚙️ Contrôles**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.session_state.simulation_active = True
        with col2:
            if st.button("⏹ STOP", use_container_width=True):
                st.session_state.simulation_active = False

        # ── Injection manuelle ──
        st.markdown("**🔧 Injection manuelle**")
        acteur_sel = st.selectbox("Acteur", list(ACTEURS.keys()))

        if st.button("📡 Envoyer une mesure", use_container_width=True):
            with st.spinner("Ingestion en cours..."):
                ingerer_mesure(acteur_sel, st.session_state.lot_actif)
            st.success("✅ Mesure ingérée dans Redis")

        st.divider()

        # ── Mode anomalie ──
        st.markdown("**⚠️ Mode Anomalie**")
        anomalie = st.toggle("Simuler rupture chaîne du froid", value=st.session_state.anomalie_active)
        st.session_state.anomalie_active = anomalie
        if anomalie:
            st.warning("Mode anomalie actif — températures hors norme seront générées")

        st.divider()

        # ── Statistiques globales ──
        st.markdown("**📊 Statistiques**")
        nb_mesures = len(st.session_state.historique_mesures)
        nb_blocs = len(st.session_state.blockchain.chaine)

        st.metric("Mesures ingérées", f"{nb_mesures:,}")
        st.metric("Blocs minés", nb_blocs)

        # Ratio conformité
        if nb_mesures > 0:
            conformes = sum(1 for m in st.session_state.historique_mesures if m["conforme"])
            ratio = (conformes / nb_mesures) * 100
            couleur = "normal" if ratio > 90 else "inverse"
            st.metric("Conformité HACCP", f"{ratio:.1f}%", delta=f"{ratio-100:.1f}%" if ratio < 100 else "✓")

        st.divider()
        st.markdown("""
        <div style='color:#445566; font-size:10px; text-align:center;'>
            Modèle BASE · Redis NoSQL · SHA-256<br>
            Proof of Work · Architecture Lambda
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# SECTION 5 — ONGLET 1 : MONITORING TEMPS RÉEL
# =============================================================================

def onglet_monitoring():
    """Dashboard de monitoring IoT en temps réel."""

    st.markdown("""
    <div class='app-header'>
        <div class='app-title'>📡 Monitoring Temps Réel</div>
        <div class='app-subtitle'>
            Flux IoT — Ingestion Big Data via Redis NoSQL (Modèle BASE) — 
            Route : Tunis → Zaghouan → Sousse → Sfax
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Simulation automatique ──
    if st.session_state.simulation_active:
        acteurs_liste = list(ACTEURS.keys())
        acteur = acteurs_liste[st.session_state.compteur_mesures % len(acteurs_liste)]
        ingerer_mesure(acteur, st.session_state.lot_actif)
        time.sleep(0.1)

    mesures = st.session_state.historique_mesures

    if not mesures:
        st.info("🚀 Appuie sur **▶ START** dans le panneau gauche ou utilise **Injection manuelle** pour démarrer la simulation.")
        # Affichage du schéma de l'architecture
        _afficher_architecture()
        return

    df = pd.DataFrame(mesures)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # ── KPIs principaux ──
    col1, col2, col3, col4 = st.columns(4)
    temp_actuelle = df["temperature"].iloc[-1]
    temp_moy = df["temperature"].mean()
    nb_anomalies = len(df[~df["conforme"]])
    blocs = len(st.session_state.blockchain.chaine) - 1

    with col1:
        delta_temp = temp_actuelle - TEMP_MAX if temp_actuelle > TEMP_MAX else None
        st.metric(
            "🌡️ Temp. Actuelle",
            f"{temp_actuelle:.2f}°C",
            delta=f"+{delta_temp:.2f}°C ⚠️" if delta_temp and delta_temp > 0 else "✓ Conforme",
            delta_color="inverse" if delta_temp and delta_temp > 0 else "normal"
        )
    with col2:
        st.metric("📊 Temp. Moyenne", f"{temp_moy:.2f}°C")
    with col3:
        st.metric("🚨 Anomalies", nb_anomalies, delta=f"/{len(df)} mesures")
    with col4:
        st.metric("⛓️ Blocs minés", blocs)

    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)

    # ── Graphique température en temps réel ──
    col_g1, col_g2 = st.columns([2, 1])

    with col_g1:
        st.markdown("**🌡️ Courbe de Température — Flux IoT en temps réel**")

        # Prendre les 100 dernières mesures pour la lisibilité
        df_recent = df.tail(100)

        fig_temp = go.Figure()

        # Zone de conformité HACCP
        fig_temp.add_hrect(
            y0=TEMP_MIN, y1=TEMP_MAX,
            fillcolor="rgba(0,255,156,0.08)",
            line_width=0,
            annotation_text="Zone HACCP",
            annotation_position="right",
            annotation_font_color="#00FF9C",
        )

        # Ligne limite haute
        fig_temp.add_hline(
            y=TEMP_MAX, line_dash="dash",
            line_color="#FF8C00", line_width=1,
            annotation_text=f"Max {TEMP_MAX}°C",
            annotation_font_color="#FF8C00",
        )

        # Courbe par acteur
        for acteur_nom, info in ACTEURS.items():
            df_acteur = df_recent[df_recent["acteur"] == acteur_nom]
            if not df_acteur.empty:
                fig_temp.add_trace(go.Scatter(
                    x=df_acteur["timestamp"],
                    y=df_acteur["temperature"],
                    mode="lines+markers",
                    name=acteur_nom,
                    line=dict(color=info["couleur"], width=2),
                    marker=dict(size=5),
                ))

        fig_temp.update_layout(
            plot_bgcolor="#0A0E1A",
            paper_bgcolor="#111827",
            font_color="#E8EDF5",
            legend=dict(bgcolor="#1C2333", bordercolor="#2A3550"),
            xaxis=dict(gridcolor="#1C2333", title="Horodatage"),
            yaxis=dict(gridcolor="#1C2333", title="Température (°C)"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
        )

        st.plotly_chart(fig_temp, use_container_width=True)

    with col_g2:
        st.markdown("**💧 Humidité par Acteur**")

        df_humid = df.groupby("acteur")["humidite"].mean().reset_index()
        couleurs_bar = [ACTEURS[a]["couleur"] for a in df_humid["acteur"] if a in ACTEURS]

        fig_bar = go.Figure(go.Bar(
            x=df_humid["acteur"].str.split(" ").str[0],  # Juste l'emoji
            y=df_humid["humidite"],
            marker_color=couleurs_bar if couleurs_bar else "#00C2FF",
            text=df_humid["humidite"].round(1).astype(str) + "%",
            textposition="outside",
        ))
        fig_bar.update_layout(
            plot_bgcolor="#0A0E1A",
            paper_bgcolor="#111827",
            font_color="#E8EDF5",
            yaxis=dict(gridcolor="#1C2333", range=[80, 100]),
            xaxis=dict(gridcolor="#1C2333"),
            margin=dict(l=5, r=5, t=10, b=10),
            height=320,
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Carte GPS ──
    st.markdown("**🗺️ Traçabilité GPS — Parcours du lot**")
    df_gps = df.dropna(subset=["gps_lat", "gps_lon"])
    if not df_gps.empty:
        df_gps_display = df_gps[["acteur", "ville", "gps_lat", "gps_lon", "temperature", "timestamp"]].copy()
        df_gps_display.columns = ["Acteur", "Ville", "Latitude", "Longitude", "Temp (°C)", "Timestamp"]

        fig_map = px.scatter_mapbox(
            df_gps_display.tail(50),
            lat="Latitude", lon="Longitude",
            color="Acteur",
            hover_data=["Ville", "Temp (°C)", "Timestamp"],
            zoom=6, height=350,
            mapbox_style="carto-darkmatter",
        )
        fig_map.update_layout(
            paper_bgcolor="#111827",
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(bgcolor="#1C2333"),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # ── Tableau des dernières mesures ──
    st.markdown("**📋 Dernières mesures ingérées (Redis Stream)**")
    df_table = df.tail(10)[["timestamp", "acteur", "ville", "temperature", "humidite", "conforme"]].copy()
    df_table["conforme"] = df_table["conforme"].map({True: "✅ OK", False: "❌ ANOMALIE"})
    df_table.columns = ["Timestamp", "Acteur", "Ville", "Temp (°C)", "Humidité (%)", "Statut HACCP"]
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # Rechargement auto si simulation active
    if st.session_state.simulation_active:
        time.sleep(0.8)
        st.rerun()


def _afficher_architecture():
    """Affiche un diagramme de l'architecture du système."""
    st.markdown("---")
    st.markdown("**🏗️ Architecture du Système FoodTrace**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style='background:#111827; border:1px solid #2A3550; border-radius:10px; padding:16px; text-align:center;'>
            <div style='font-size:28px'>📡</div>
            <div style='color:#00FF9C; font-weight:700; margin:8px 0;'>Couche IoT</div>
            <div style='color:#8899BB; font-size:12px;'>Capteurs Temp/Humidité/GPS<br>→ Velocity (Big Data)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='background:#111827; border:1px solid #2A3550; border-radius:10px; padding:16px; text-align:center;'>
            <div style='font-size:28px'>⚡</div>
            <div style='color:#00C2FF; font-weight:700; margin:8px 0;'>Couche Redis (NoSQL)</div>
            <div style='color:#8899BB; font-size:12px;'>Modèle BASE<br>Ingestion sub-milliseconde</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style='background:#111827; border:1px solid #2A3550; border-radius:10px; padding:16px; text-align:center;'>
            <div style='font-size:28px'>⛓️</div>
            <div style='color:#B06EFF; font-weight:700; margin:8px 0;'>Couche Blockchain</div>
            <div style='color:#8899BB; font-size:12px;'>SHA-256 · Proof of Work<br>→ Veracity (5ème V)</div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# SECTION 6 — ONGLET 2 : REGISTRE BLOCKCHAIN
# =============================================================================

def onglet_blockchain():
    """Affichage du registre blockchain et des blocs minés."""

    st.markdown("""
    <div class='app-header'>
        <div class='app-title'>⛓️ Registre Blockchain</div>
        <div class='app-subtitle'>
            Chaque bloc scelle le hash SHA-256 d'un lot de 10 mesures IoT — Proof of Work (3 zéros)
        </div>
    </div>
    """, unsafe_allow_html=True)

    bc = st.session_state.blockchain
    chaine = bc.chaine

    # ── Métriques chaîne ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔢 Blocs totaux", len(chaine))
    with col2:
        st.metric("⚙️ Difficulté PoW", f"{bc.DIFFICULTE} zéros")
    with col3:
        nonces = [b.nonce for b in chaine[1:]] if len(chaine) > 1 else [0]
        st.metric("🔄 Nonce moyen", f"{sum(nonces)//max(len(nonces),1):,}")
    with col4:
        integre, _ = bc.verifier_integrite()
        st.metric("🛡️ Intégrité", "✅ Valide" if integre else "❌ Corrompue")

    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)

    if len(chaine) == 1:
        st.info("⛏️ Aucun bloc miné pour l'instant. Génère au moins **10 mesures** pour déclencher le minage d'un bloc.")
        return

    # ── Affichage des blocs ──
    st.markdown(f"**📜 {len(chaine)} blocs dans la chaîne (du plus récent au plus ancien)**")

    for bloc in reversed(chaine):
        couleur_acteur = ACTEURS.get(bloc.acteur, {}).get("couleur", "#8899BB")

        if bloc.index == 0:
            label_acteur = "BLOC GENÈSE"
            couleur_acteur = "#8899BB"
        else:
            label_acteur = bloc.acteur

        st.markdown(f"""
        <div class='bloc-card'>
            <div class='bloc-index'>
                {'🧱 GENÈSE' if bloc.index == 0 else f'⛓️ BLOC #{bloc.index}'}
                <span style='font-size:13px; color:{couleur_acteur}; margin-left:12px;
                             background:rgba(0,0,0,0.3); padding:2px 10px; border-radius:20px;'>
                    {label_acteur}
                </span>
                <span style='font-size:12px; color:#445566; float:right;'>{bloc.timestamp[:19]}</span>
            </div>
            <div style='margin:8px 0; color:#8899BB; font-size:11px;'>
                📦 Lot : <span style='color:#E8EDF5;'>{bloc.lot_id}</span> &nbsp;|&nbsp;
                🔄 Nonce : <span style='color:#FF8C00;'>{bloc.nonce:,}</span>
            </div>
            <div style='margin:6px 0;'>
                <span style='color:#8899BB;'>Hash données IoT :</span><br>
                <span class='bloc-hash'>🔐 {bloc.donnees_hash}</span>
            </div>
            <div style='margin:6px 0;'>
                <span style='color:#8899BB;'>Hash de ce bloc :</span><br>
                <span class='bloc-hash' style='color:#00C2FF;'>✅ {bloc.hash_bloc}</span>
            </div>
            <div style='margin:6px 0;'>
                <span style='color:#8899BB;'>Hash bloc précédent :</span><br>
                <span class='bloc-prev'>🔗 {bloc.hash_precedent[:64]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Graphique des nonces (PoW) ──
    if len(chaine) > 2:
        st.markdown("**⚙️ Effort de minage par bloc (Proof of Work)**")
        df_pow = pd.DataFrame([
            {"Bloc": f"#{b.index}", "Nonce": b.nonce}
            for b in chaine[1:]
        ])
        fig_pow = go.Figure(go.Bar(
            x=df_pow["Bloc"], y=df_pow["Nonce"],
            marker_color="#00C2FF",
            text=df_pow["Nonce"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig_pow.update_layout(
            plot_bgcolor="#0A0E1A", paper_bgcolor="#111827",
            font_color="#E8EDF5",
            yaxis=dict(gridcolor="#1C2333", title="Nonce (tentatives)"),
            xaxis=dict(title="Bloc"),
            margin=dict(l=5, r=5, t=10, b=10),
            height=250,
        )
        st.plotly_chart(fig_pow, use_container_width=True)


# =============================================================================
# SECTION 7 — ONGLET 3 : AUDIT & DÉTECTION DE FRAUDE (L'EFFET WAHOU)
# =============================================================================

def onglet_audit():
    """Interface d'audit et de détection de fraude par comparaison blockchain."""

    st.markdown("""
    <div class='app-header'>
        <div class='app-title'>🔍 Audit & Détection de Fraude</div>
        <div class='app-subtitle'>
            Modifiez les données historiques — La Blockchain détectera immédiatement toute altération
        </div>
    </div>
    """, unsafe_allow_html=True)

    bc = st.session_state.blockchain
    mesures = st.session_state.historique_mesures

    if len(mesures) < 10 or len(bc.chaine) < 2:
        st.warning("⚠️ Génère au moins **10 mesures** (1 bloc miné) pour utiliser l'outil d'audit.")
        return

    # ── Sélection du bloc à auditer ──
    st.markdown("### 🎯 Sélectionner un bloc à auditer")
    blocs_disponibles = [f"Bloc #{b.index} — {b.acteur} — {b.timestamp[:19]}"
                         for b in bc.chaine[1:]]
    bloc_sel_str = st.selectbox("Choisir un bloc", blocs_disponibles)
    bloc_index = int(bloc_sel_str.split("#")[1].split(" ")[0])
    bloc_selectionne = bc.chaine[bloc_index]

    # ── Affichage du contenu du bloc ──
    col_info, col_action = st.columns([1, 1])

    with col_info:
        st.markdown("**📋 Contenu enregistré dans la Blockchain**")
        st.code(f"""
Bloc Index    : #{bloc_selectionne.index}
Lot ID        : {bloc_selectionne.lot_id}
Acteur        : {bloc_selectionne.acteur}
Timestamp     : {bloc_selectionne.timestamp}
Hash données  : {bloc_selectionne.donnees_hash[:32]}...
Hash du bloc  : {bloc_selectionne.hash_bloc[:32]}...
Hash préc.    : {bloc_selectionne.hash_precedent[:32]}...
Nonce (PoW)   : {bloc_selectionne.nonce:,}
        """, language="yaml")

    with col_action:
        st.markdown("**🔧 Simuler une falsification de données**")
        st.markdown("""
        <div style='background:#1C2333; border:1px solid #FF8C00; border-radius:10px;
                    padding:14px; margin-bottom:16px; font-size:13px; color:#FF8C00;'>
            ⚠️ <strong>Scénario de fraude :</strong> Un opérateur tente de modifier 
            rétroactivement une température pour cacher une rupture de chaîne du froid.
        </div>
        """, unsafe_allow_html=True)

        # Choix d'une mesure à falsifier
        debut_index = (bloc_index - 1) * 10
        mesures_du_bloc = mesures[debut_index:debut_index + 10]

        if mesures_du_bloc:
            mesure_idx = st.slider(
                "Mesure à falsifier (dans le lot)",
                0, len(mesures_du_bloc) - 1, 0
            )
            mesure_cible = mesures_du_bloc[mesure_idx]

            st.markdown(f"""
            <div style='font-size:12px; color:#8899BB; font-family: monospace;'>
                Mesure #{mesure_idx} — {mesure_cible['acteur']}<br>
                Temp originale : <span style='color:#00FF9C; font-weight:700;'>
                    {mesure_cible['temperature']}°C</span>
            </div>
            """, unsafe_allow_html=True)

            nouvelle_temp = st.number_input(
                "Nouvelle température falsifiée (°C)",
                min_value=-5.0, max_value=30.0,
                value=float(round(mesure_cible["temperature"] + 7.5, 1)),
                step=0.1,
            )

            if st.button("🚨 MODIFIER LES DONNÉES (Simuler la fraude)", type="primary", use_container_width=True):
                # Modification de la donnée dans le buffer (simule une attaque sur Redis)
                mesures_falsifiees = list(mesures_du_bloc)
                mesures_falsifiees[mesure_idx] = {
                    **mesure_cible,
                    "temperature": nouvelle_temp
                }

                # Calcul du nouveau hash après falsification
                hash_falsifie = bc.hash_donnees(mesures_falsifiees)
                hash_original = bloc_selectionne.donnees_hash

                # Comparaison avec la Blockchain (immuable)
                if hash_falsifie != hash_original:
                    st.session_state.fraude_detectee = True
                    st.session_state.detail_fraude = {
                        "bloc_index": bloc_index,
                        "acteur": bloc_selectionne.acteur,
                        "temp_originale": mesure_cible["temperature"],
                        "temp_falsifiee": nouvelle_temp,
                        "hash_original": hash_original,
                        "hash_falsifie": hash_falsifie,
                        "mesure_idx": mesure_idx,
                    }
                else:
                    st.session_state.fraude_detectee = False

    # ─────────────────────────────────────────
    # 💥 L'EFFET WAHOU — ALERTE DE FRAUDE
    # ─────────────────────────────────────────
    st.markdown("---")

    if st.session_state.fraude_detectee and st.session_state.detail_fraude:
        d = st.session_state.detail_fraude

        st.markdown(f"""
        <div class='alerte-fraude'>
            <div class='alerte-titre'>🚨 CORRUPTION DÉTECTÉE — FRAUDE CONFIRMÉE</div>
            <div style='color:#FF6666; font-size:15px; margin-top:8px;'>
                Le hash des données ne correspond plus au hash enregistré sur la Blockchain
            </div>
            <div class='alerte-details'>
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br><br>
                🎯 Bloc ciblé : <strong>#{d['bloc_index']}</strong> &nbsp;|&nbsp;
                Acteur : <strong>{d['acteur']}</strong><br><br>
                🌡️ Température originale : <span style='color:#00FF9C; font-size:16px; font-weight:700;'>
                    {d['temp_originale']}°C</span>
                &nbsp;→&nbsp;
                Falsifiée : <span style='color:#FF3B3B; font-size:16px; font-weight:700;'>
                    {d['temp_falsifiee']}°C</span><br><br>
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br><br>
                📌 Hash Blockchain (immuable) :<br>
                <span style='color:#00FF9C;'>{d['hash_original']}</span><br><br>
                💀 Hash données falsifiées :<br>
                <span style='color:#FF3B3B;'>{d['hash_falsifie']}</span><br><br>
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br>
                ✅ La Blockchain a rendu cette tentative de fraude <strong>impossible à dissimuler</strong>.<br>
                Ce lot ne peut pas être validé pour la distribution.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Graphique comparaison visuelle
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**📊 Visualisation de la tentative de falsification**")

        fig_fraude = go.Figure()

        temps = list(range(len(mesures_du_bloc)))
        temps_orig = [m["temperature"] for m in mesures_du_bloc]
        temps_fals = list(temps_orig)
        if d["mesure_idx"] < len(temps_fals):
            temps_fals[d["mesure_idx"]] = d["temp_falsifiee"]

        fig_fraude.add_trace(go.Scatter(
            x=temps, y=temps_orig,
            mode="lines+markers",
            name="🟢 Données originales (Blockchain)",
            line=dict(color="#00FF9C", width=2.5),
            marker=dict(size=8),
        ))
        fig_fraude.add_trace(go.Scatter(
            x=temps, y=temps_fals,
            mode="lines+markers",
            name="🔴 Données falsifiées (Redis modifié)",
            line=dict(color="#FF3B3B", width=2.5, dash="dash"),
            marker=dict(size=8, symbol="x"),
        ))

        # Point de falsification
        fig_fraude.add_trace(go.Scatter(
            x=[d["mesure_idx"]],
            y=[d["temp_falsifiee"]],
            mode="markers",
            name="💀 Point falsifié",
            marker=dict(size=16, color="#FF3B3B", symbol="star"),
        ))

        fig_fraude.add_hrect(
            y0=TEMP_MIN, y1=TEMP_MAX,
            fillcolor="rgba(0,255,156,0.07)", line_width=0,
            annotation_text="Zone HACCP conforme",
            annotation_font_color="#00FF9C",
        )

        fig_fraude.update_layout(
            plot_bgcolor="#0A0E1A", paper_bgcolor="#111827",
            font_color="#E8EDF5",
            xaxis=dict(gridcolor="#1C2333", title="Index de la mesure dans le lot"),
            yaxis=dict(gridcolor="#1C2333", title="Température (°C)"),
            legend=dict(bgcolor="#1C2333"),
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_fraude, use_container_width=True)

        if st.button("🔄 Réinitialiser la détection"):
            st.session_state.fraude_detectee = False
            st.session_state.detail_fraude = {}
            st.rerun()

    else:
        # Affichage si pas de fraude détectée
        if not st.session_state.detail_fraude:
            st.markdown("""
            <div style='background:#111827; border:1px solid #2A3550; border-radius:12px;
                        padding:24px; text-align:center; color:#8899BB;'>
                <div style='font-size:40px; margin-bottom:12px;'>🔐</div>
                <div style='font-size:16px; font-weight:600;'>Système en attente d'audit</div>
                <div style='font-size:13px; margin-top:8px;'>
                    Sélectionne un bloc et utilise le panneau de droite<br>pour simuler une tentative de falsification.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='badge-ok'>
                <div style='font-size:40px;'>✅</div>
                <div class='badge-ok-titre'>Données intègres — Aucune falsification</div>
                <div style='color:#8899BB; font-size:13px; margin-top:8px;'>
                    Le hash calculé correspond exactement au hash enregistré sur la Blockchain.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Vérification globale de la chaîne ──
    st.markdown("---")
    st.markdown("### 🛡️ Vérification Globale de la Chaîne")

    if st.button("🔍 Lancer la vérification complète de la Blockchain", use_container_width=True):
        with st.spinner("Vérification de tous les blocs..."):
            time.sleep(1)  # Effet visuel
            integre, message = bc.verifier_integrite()

        if integre:
            st.markdown(f"""
            <div class='badge-ok'>
                <div style='font-size:36px;'>🔒</div>
                <div class='badge-ok-titre'>Blockchain Intègre</div>
                <div style='color:#8899BB; font-size:13px; margin-top:8px;'>
                    {len(bc.chaine)} blocs vérifiés — {message}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alerte-fraude'>
                <div class='alerte-titre'>⚠️ CHAÎNE COMPROMISE</div>
                <div class='alerte-details'>{message}</div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# SECTION 8 — APPLICATION PRINCIPALE
# =============================================================================

def main():
    """Point d'entrée principal de l'application."""

    # Initialisation de l'état
    initialiser_etat()

    # Sidebar
    afficher_sidebar()

    # Onglets principaux
    tab1, tab2, tab3 = st.tabs([
        "📡  Monitoring Temps Réel",
        "⛓️  Registre Blockchain",
        "🔍  Audit & Détection de Fraude",
    ])

    with tab1:
        onglet_monitoring()

    with tab2:
        onglet_blockchain()

    with tab3:
        onglet_audit()


if __name__ == "__main__":
    main()
