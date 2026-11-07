import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score,
                             classification_report, confusion_matrix)

df = pd.read_excel("data/incidents.xlsx")

X = df["description"]    
y = df["cause_vraie"]    


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print(len(X_train), "lignes pour l'entraînement")
print(len(X_test), "lignes pour le test")

#
modele = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
    ("clf", LogisticRegression(max_iter=1000)),
])


modele.fit(X_train, y_train)


y_pred = modele.predict(X_test)


print("\nAccuracy :", round(accuracy_score(y_test, y_pred), 3))
print("F1 macro :", round(f1_score(y_test, y_pred, average="macro"), 3))
print("\nRapport par classe :")
print(classification_report(y_test, y_pred))
print("Matrice de confusion :")
print(confusion_matrix(y_test, y_pred))


scores = cross_val_score(modele, X, y, cv=5, scoring="f1_macro")
print("\nCV F1 macro (5 plis) :", round(scores.mean(), 3))


joblib.dump(modele, "data/modele_ml.joblib")
print("Modèle sauvegardé dans data/modele_ml.joblib")