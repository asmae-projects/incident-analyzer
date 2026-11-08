from datetime import datetime
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches


def graphique_pareto(data):
    comptes = data["cause"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(comptes.index, comptes.values, color="#1F4E79")
    ax.set_title("Pareto des causes")
    ax.set_ylabel("Nombre d'incidents")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def generer_rapport(data, chemin):
    doc = Document()
    doc.add_heading("Rapport d'incidents industriels", level=0)

    debut = data["date"].min().strftime("%d/%m/%Y")
    fin = data["date"].max().strftime("%d/%m/%Y")
    doc.add_paragraph(f"Période : {debut} au {fin}")
    doc.add_paragraph(f"Généré le {datetime.now():%d/%m/%Y}")

    # KPI
    doc.add_heading("Indicateurs clés", level=1)
    pct = (data["gravite"] == "Critique").mean() * 100
    doc.add_paragraph(f"Nombre d'incidents : {len(data)}")
    doc.add_paragraph(f"Durée d'arrêt totale : {int(data['duree_arret_min'].sum())} min")
    doc.add_paragraph(f"Part d'incidents critiques : {pct:.1f} %")

    # Pareto + top 3
    doc.add_heading("Causes principales", level=1)
    doc.add_picture(graphique_pareto(data), width=Inches(6))
    for cause, n in data["cause"].value_counts().head(3).items():
        doc.add_paragraph(f"{cause} : {n} incidents", style="List Bullet")

    # Incidents critiques
    doc.add_heading("Incidents critiques", level=1)
    crit = data[data["gravite"] == "Critique"]
    table = doc.add_table(rows=1, cols=5)
    table.style = "Light Grid Accent 1"
    for i, titre in enumerate(["ID", "Date", "Machine", "Cause", "Action recommandée"]):
        table.rows[0].cells[i].text = titre
    for _, r in crit.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(r["id"])
        cells[1].text = r["date"].strftime("%d/%m/%Y")
        cells[2].text = str(r["machine"])
        cells[3].text = str(r["cause"])
        cells[4].text = str(r["action"])

    doc.save(chemin)
    return chemin