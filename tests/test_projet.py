import sys
from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from schema import ReponseIncident
from llm_classifier import parser_reponse
from report import generer_rapport


def test_schema_rejette_reponse_invalide():
    with pytest.raises(ValidationError):
        ReponseIncident(cause="Magie", gravite="Critique", action="x")


def test_parsing_json_mal_forme():
    with pytest.raises(Exception):
        parser_reponse("{cause: pas du json")


def test_parsing_json_valide_avec_balises():
    texte = '```json\n{"cause": "Mécanique", "gravite": "Faible", "action": "x"}\n```'
    assert parser_reponse(texte)["cause"] == "Mécanique"


def test_pipeline_ml_predit():
    import joblib
    racine = Path(__file__).resolve().parent.parent
    modele = joblib.load(racine / "data" / "modele_ml.joblib")
    assert modele.predict(["Presse-01 : roulement bruyant"])[0] is not None


def test_rapport_word_non_vide(tmp_path):
    data = pd.DataFrame({
        "id": ["INC-0001"],
        "date": [pd.Timestamp("2026-08-01")],
        "machine": ["Presse-01"],
        "cause": ["Mécanique"],
        "gravite": ["Critique"],
        "duree_arret_min": [120],
        "action": ["Remplacer le roulement"],
    })
    chemin = tmp_path / "rapport.docx"
    generer_rapport(data, chemin)
    assert chemin.stat().st_size > 0
    