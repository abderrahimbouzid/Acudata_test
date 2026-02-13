import os
from dotenv import load_dotenv
import google.generativeai as genai

# Charger la clé API
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Pas de clé API trouvée dans .env")
    exit()

# Configurer Google AI
genai.configure(api_key=api_key)

print(f"✅ Clé trouvée. Interrogation de Google pour les modèles d'embedding...")

try:
    found = False
    for m in genai.list_models():
        # On cherche les modèles capables de faire de l'embedding ('embedContent')
        if 'embedContent' in m.supported_generation_methods:
            print(f"👉 Modèle disponible : {m.name}")
            found = True
    
    if not found:
        print("⚠️ Aucun modèle d'embedding trouvé. Vérifiez les permissions de votre clé API.")

except Exception as e:
    print(f"❌ Erreur lors de la connexion : {e}")