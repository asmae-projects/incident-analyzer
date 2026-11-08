import time
import json
import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from llm_classifier import classify

RACINE = Path(__file__).resolve().parent.parent


df = pd.read_excel(RACINE / "data" / "incidents.xlsx")
_, X_test, _, y_test = train_test_split(
    df["description"], df["cause_vraie"],
    test_size=0.2, stratify=df["cause_vraie"], random_state=42
)


modele = joblib.load(RACINE / "data" / "modele_ml.joblib")
debut = time.time()
pred_ml = modele.predict(X_test)
temps_ml = time.time() - debut


debut = time.time()
pred_llm = [classify(d)["cause"] for d in X_test]
temps_llm = time.time() - debut


def metriques(y_vrai, y_pred):
    return (round(accuracy_score(y_vrai, y_pred), 3),
            round(f1_score(y_vrai, y_pred, average="macro"), 3))

acc_ml, f1_ml = metriques(y_test, pred_ml)
acc_llm, f1_llm = metriques(y_test, pred_llm)

tableau = pd.DataFrame({
    "Approche": ["ML (TF-IDF + LogReg)", "LLM (Gemini)"],
    "Accuracy": [acc_ml, acc_llm],
    "F1 macro": [f1_ml, f1_llm],
    "Temps (s)": [round(temps_ml, 3), round(temps_llm, 1)],
    "Coût estimé": ["0 $", "0 $ (quota gratuit)"],
})
print(tableau.to_string(index=False))


res = pd.DataFrame({
    "description": X_test.values,
    "vraie": y_test.values,
    "ml": pred_ml,
    "llm": pred_llm,
})
print("\n--- 5 erreurs du ML ---")
print(res[res["vraie"] != res["ml"]].head(5).to_string(index=False))
print("\n--- 5 erreurs du LLM ---")
print(res[res["vraie"] != res["llm"]].head(5).to_string(index=False))


res.to_csv(RACINE / "data" / "resultats_test.csv", index=False)
tableau.to_csv(RACINE / "data" / "comparaison.csv", index=False)