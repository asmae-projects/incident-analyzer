import os
import json
import hashlib
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from pydantic import ValidationError

from schema import ReponseIncident

load_dotenv()

RACINE = Path(__file__).resolve().parent.parent
CACHE_FILE = RACINE / "data" / "cache_llm.json"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELE = os.getenv("GEMINI_MODEL")

PROMPT = """Tu es un expert en maintenance industrielle.
Classe l'incident suivant.

Causes possibles : Mécanique, Électrique, Qualité matière, Procédure/Opérateur, Logiciel/Automate, Maintenance.
Gravités possibles : Faible, Moyenne, Critique.

Réponds uniquement en JSON, sans texte autour, au format :
{{"cause": "...", "gravite": "...", "action": "..."}}

Exemple 1 :
Incident : Presse-01 : roulement bruyant, vibrations anormales
{{"cause": "Mécanique", "gravite": "Moyenne", "action": "Remplacer le roulement"}}

Exemple 2 :
Incident : Robot-03 : capteur non reconnu par le PLC
{{"cause": "Logiciel/Automate", "gravite": "Faible", "action": "Redémarrer l'automate et vérifier le capteur"}}

Incident : {description}
"""


def charger_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def sauver_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2),
                          encoding="utf-8")


def parser_reponse(texte):
    """Nettoie et valide la réponse du LLM. Lève une erreur si invalide."""
    texte = texte.strip().replace("```json", "").replace("```", "").strip()
    return ReponseIncident(**json.loads(texte)).model_dump()


def appeler_llm(description):
    rep = client.models.generate_content(
        model=MODELE,
        contents=PROMPT.format(description=description),
    )
    return rep.text


def classify(description):
    cache = charger_cache()
    cle = hashlib.md5(description.encode("utf-8")).hexdigest()
    if cle in cache:
        
        return cache[cle]

    resultat = {"cause": "Inconnu", "gravite": "Inconnu", "action": ""}
    for essai in range(2):
        try:
            resultat = parser_reponse(appeler_llm(description))
            break
        except (json.JSONDecodeError, ValidationError, TypeError):
            continue
        except Exception as e:  
            print("Erreur API :", e)
            time.sleep(5)

    cache[cle] = resultat
    sauver_cache(cache)
    time.sleep(1) 
    return resultat


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_excel(RACINE / "data" / "incidents.xlsx").head(20)
    for _, ligne in df.iterrows():
        r = classify(ligne["description"])
        print(ligne["cause_vraie"], "->", r["cause"], "|", r["gravite"])