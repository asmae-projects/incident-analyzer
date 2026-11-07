import random
from datetime import datetime, timedelta
import pandas as pd

random.seed(42)

CAUSES = ["Mécanique", "Électrique", "Qualité matière",
          "Procédure/Opérateur", "Logiciel/Automate", "Maintenance"]
POIDS_CAUSES = [25, 20, 15, 15, 15, 10]  
GRAVITES = ["Faible", "Moyenne", "Critique"]
POIDS_GRAVITES = [50, 35, 15]
MACHINES = ["Presse-01", "Sertisseuse-02", "Robot-03", "Convoyeur-04",
            "Soudeuse-05", "Perceuse-06"]
LIGNES = ["Ligne-A", "Ligne-B", "Ligne-C"]

DUREES = {"Faible": (5, 20), "Moyenne": (20, 90), "Critique": (90, 360)}

TEMPLATES = {
    "Mécanique": [
        "{machine} : roulement bruyant, vibrations anormales",
        "{machine} arrêtée, courroie cassée",
        "{machine} : fuite d'huile sur le vérin, pression basse",
        "{machine} : axe grippé, mouvement bloqué",
    ],
    "Électrique": [
        "{machine} : moteur en panne, disjoncteur déclenché",
        "{machine} : câble d'alimentation sectionné",
        "{machine} : surchauffe du moteur, odeur de brûlé",
        "{machine} : coupure de courant, contacteur défectueux",
    ],
    "Qualité matière": [
        "{machine} : matière première non conforme, pièces rebutées",
        "{machine} : lot de tôle avec défaut d'épaisseur",
        "{machine} : pièces fournisseur hors tolérance",
        "{machine} : matière humide, soudure de mauvaise qualité",
    ],
    "Procédure/Opérateur": [
        "{machine} : mauvais réglage par l'opérateur",
        "{machine} : procédure de démarrage non respectée",
        "{machine} : erreur de manipulation lors du changement de série",
        "{machine} : contrôle de début de poste oublié",
    ],
    "Logiciel/Automate": [
        "{machine} : automate bloqué, erreur de programme",
        "{machine} : capteur non reconnu par le PLC",
        "{machine} : écran HMI figé, recette introuvable",
        "{machine} : défaut de communication avec le superviseur",
    ],
    "Maintenance": [
        "{machine} : graissage non effectué, maintenance préventive en retard",
        "{machine} : filtre colmaté, nettoyage oublié",
        "{machine} : usure d'un outil non remplacé à temps",
        "{machine} : intervention préventive reportée, panne en production",
    ],
}

REMPLACEMENTS = {
    "contrôle": "ctrl",
    "moteur en panne": "moteur HS",
    "automate": "PLC",
    "capteur": "sensor",
    "arrêtée": "stopped",
    "maintenance": "maint.",
    "opérateur": "op.",
}


def generer_description(cause, machine):
    phrase = random.choice(TEMPLATES[cause])
    return phrase.format(machine=machine)


def ajouter_bruit(texte):
    
    for mot, remplacement in REMPLACEMENTS.items():
        if mot in texte and random.random() < 0.5:
            texte = texte.replace(mot, remplacement)
    
    if random.random() < 0.15 and len(texte) > 10:
        pos = random.randint(8, len(texte) - 1)
        texte = texte[:pos] + texte[pos + 1:]
    return texte


def generer_incident(i):
    cause = random.choices(CAUSES, weights=POIDS_CAUSES)[0]
    gravite = random.choices(GRAVITES, weights=POIDS_GRAVITES)[0]
    machine = random.choice(MACHINES)
    ligne = random.choice(LIGNES)

    description = generer_description(cause, machine)

   
    if random.random() < 0.10:
        autre_cause = random.choice([c for c in CAUSES if c != cause])
        if random.random() < 0.5:
            
            description += ", " + random.choice(TEMPLATES[autre_cause]).split(": ")[1]
        else:
           
            cause = autre_cause

    description = ajouter_bruit(description)

    date = datetime(2026, 8, 1) + timedelta(days=random.randint(0, 89))
    mini, maxi = DUREES[gravite]

    return {
        "id": f"INC-{i:04d}",
        "date": date.strftime("%Y-%m-%d"),
        "machine": machine,
        "ligne": ligne,
        "description": description,
        "duree_arret_min": random.randint(mini, maxi),
        "cause_vraie": cause,
        "gravite_vraie": gravite,
    }


def main():
    incidents = [generer_incident(i) for i in range(1, 301)]
    df = pd.DataFrame(incidents)
    df = df.sort_values("date").reset_index(drop=True)
    df.to_excel("data/incidents.xlsx", index=False)
    print(f"{len(df)} incidents générés dans data/incidents.xlsx")
    print(df["cause_vraie"].value_counts())


if __name__ == "__main__":
    main()