import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RACINE = Path(__file__).resolve().parent
sys.path.append(str(RACINE / "src"))

from llm_classifier import classify  # noqa: E402
from report import generer_rapport  # noqa: E402

st.set_page_config(page_title="Analyseur d'incidents", layout="wide")
st.title("Analyseur de rapports d'incidents industriels")

# 1. Chargement du fichier
fichier = st.file_uploader("Fichier Excel d'incidents", type="xlsx")
if fichier is not None:
    df = pd.read_excel(fichier)
else:
    df = pd.read_excel(RACINE / "data" / "incidents.xlsx")
    st.caption("Fichier par défaut : data/incidents.xlsx")

df = df.head(60)  # temporaire : jeu déjà en cache, pour tester vite

# 2. Bouton Analyser (classement LLM, avec cache)
if st.button("Analyser"):
    resultats = []
    barre = st.progress(0.0)
    for i, desc in enumerate(df["description"]):
        resultats.append(classify(desc))
        barre.progress((i + 1) / len(df))
    df["cause"] = [r["cause"] for r in resultats]
    df["gravite"] = [r["gravite"] for r in resultats]
    df["action"] = [r["action"] for r in resultats]
    st.session_state["df_classe"] = df
    st.success("Analyse terminée")

if "df_classe" not in st.session_state:
    st.info("Clique sur « Analyser » pour classer les incidents "
            "(les résultats déjà en cache sont instantanés).")
    st.stop()

data = st.session_state["df_classe"].copy()
data["date"] = pd.to_datetime(data["date"])

# 3. Filtres
st.sidebar.header("Filtres")
machines = st.sidebar.multiselect("Machine", sorted(data["machine"].unique()))
lignes = st.sidebar.multiselect("Ligne", sorted(data["ligne"].unique()))
gravites = st.sidebar.multiselect("Gravité", sorted(data["gravite"].unique()))
d_min, d_max = data["date"].min().date(), data["date"].max().date()
periode = st.sidebar.date_input("Période", (d_min, d_max))

if machines:
    data = data[data["machine"].isin(machines)]
if lignes:
    data = data[data["ligne"].isin(lignes)]
if gravites:
    data = data[data["gravite"].isin(gravites)]
if len(periode) == 2:
    data = data[(data["date"].dt.date >= periode[0]) &
                (data["date"].dt.date <= periode[1])]

# 4. KPI
c1, c2, c3 = st.columns(3)
c1.metric("Incidents", len(data))
c2.metric("Arrêt total (min)", int(data["duree_arret_min"].sum()))
pct = (data["gravite"] == "Critique").mean() * 100 if len(data) else 0
c3.metric("% critiques", f"{pct:.1f} %")

# 5. Causes d'incidents
pareto = data["cause"].value_counts().reset_index()
pareto.columns = ["cause", "nombre"]

fig = px.bar(pareto, x="cause", y="nombre", title="Incidents par cause",
             color_discrete_sequence=["#1F4E79"])
fig.update_layout(xaxis_title=None, yaxis_title="Nombre d'incidents")
st.plotly_chart(fig, use_container_width=True)

# 6. Tableau des incidents classés
st.subheader("Incidents classés")
st.dataframe(data[["id", "date", "machine", "ligne", "description",
                   "duree_arret_min", "cause", "gravite", "action"]],
             use_container_width=True)

# 7. Rapport Word
if st.button("Générer le rapport Word"):
    chemin = RACINE / "data" / "rapport_incidents.docx"
    generer_rapport(data, chemin)
    with open(chemin, "rb") as f:
        st.download_button("Télécharger le rapport", f,
                           file_name="rapport_incidents.docx")