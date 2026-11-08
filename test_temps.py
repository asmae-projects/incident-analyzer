import os, time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
debut = time.time()
rep = client.models.generate_content(
    model=os.getenv("GEMINI_MODEL"),
    contents="Réponds uniquement : OK",
)
print(rep.text, "|", round(time.time() - debut, 1), "secondes")