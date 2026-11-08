from typing import Literal
from pydantic import BaseModel

Cause = Literal["Mécanique", "Électrique", "Qualité matière",
                "Procédure/Opérateur", "Logiciel/Automate", "Maintenance",
                "Inconnu"]
Gravite = Literal["Faible", "Moyenne", "Critique", "Inconnu"]


class ReponseIncident(BaseModel):
    cause: Cause
    gravite: Gravite
    action: str