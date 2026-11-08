# Analyseur de rapports d'incidents industriels

Ce projet compare deux approches pour trier et analyser automatiquement des rapports d'incidents industriels : un modèle de Machine Learning classique (TF-IDF + régression logistique) et un LLM (Gemini). 

L'application extrait la **cause**, la **gravité** et l'**action corrective** pour chaque rapport, affiche les statistiques sur un tableau de bord Streamlit et génère un compte-rendu au format Word.

---

## Architecture du pipeline

```text
incidents.xlsx ─┬─► LLM (Gemini + validation Pydantic + cache local) ─┐
                │                                                     ├─► Évaluation ─► Dashboard Streamlit & Rapport .docx
                └─► ML classique (TF-IDF + Régression Logistique) ────┘
```

---

## Benchmarks & Résultats

Évaluation réalisée sur un jeu de test commun de **60 incidents** (découpage stratifié 80/20, `random_state=42`).

| Modèle | Accuracy | F1-score (macro) | Temps d'exécution | Coût |
| :--- | :---: | :---: | :---: | :---: |
| **ML** (TF-IDF + LogReg) | **0.967** | **0.964** | **0,002 s** | 0 \$ (local) |
| **LLM** (Gemini Flash-Lite) | 0.850 | 0.866 | 491 s* | 0 \$ (Free Tier) |

*\*Le temps d'exécution du LLM inclut les temps de pause forcés pour respecter la limite du quota gratuit (15 requêtes/minute).*

### Ce qu'il faut retenir des tests
* **Bruit dans les données :** Les deux seules erreurs du modèle ML viennent d'erreurs volontaires injectées dans le dataset (ex. un *« câble d'alimentation sectionné »* étiqueté comme panne *Mécanique*). Le modèle a en réalité trouvé la bonne cause malgré la mauvaise étiquette.
* **Hésitations du LLM :** Gemini a parfois du mal à trancher entre *Électrique* et *Mécanique* sur des cas ambigus comme une surchauffe moteur.
* **Biais du dataset synthétique :** Le ML surclasse le LLM ici uniquement parce que les phrases générées suivent des structures assez répétitives. Sur de vrais rapports terrain, beaucoup plus variés et mal rédigés, le LLM garderait probablement l'avantage grâce à sa capacité de généralisation.

---

## Limites actuelles

* **Données artificielles :** Le dataset est 100 % synthétique. Les scores obtenus valident le pipeline, pas une mise en production directe.
* **Taille de l'échantillon :** Avec 60 lignes de test, un écart de quelques prédictions fait vite bouger les pourcentages.
* **Bride API :** Le script LLM tourne au ralenti à cause du *rate limiting* de l'API gratuite. Pour éviter d'exploser les quotas, le dashboard Streamlit se limite aux 60 premiers incidents déjà mis en cache.

---

## Installation et utilisation

### 1. Cloner le dépôt et installer les dépendances
```bash
git clone https://github.com/asmae-projects/incident-analyzer.git
cd incident-analyzer

python -m venv venv
# Sous Windows :
venv\Scripts\activate
# Sous Linux/macOS :
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurer l'environnement
Crée un fichier `.env` à la racine du projet avec ta clé API Google :
```env
GEMINI_API_KEY=ta_cle_api_ici
GEMINI_MODEL=gemini-3.1-flash-lite
```

### 3. Lancer les scripts
```bash
python src/generate_data.py   # Génère le fichier Excel d'incidents
python src/ml_classifier.py   # Entraîne et sauvegarde le modèle ML
python src/evaluate.py        # Lance le comparatif ML vs LLM
streamlit run app.py          # Ouvre l'interface web
pytest                        # Exécute les tests unitaires
```

---

## Arborescence

```text
├── data/       # Fichier incidents.xlsx et métriques d'évaluation
├── src/        # Scripts : génération, schémas Pydantic, modèles et export Word
├── tests/      # Tests unitaires (pytest)
├── docs/       # Captures d'écran pour la documentation
└── app.py      # Application principale Streamlit
```

---

## Aperçu

### Tableau de bord Streamlit
![Tableau de bord](docs/dashboard.png)

### Exemple de rapport Word généré
![Rapport Word](docs/rapport.png)
