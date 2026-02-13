import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import create_client

load_dotenv()

# Connexion
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

base_path = "data"
documents_to_insert = []

# Parcours des dossiers
for folder in ["client_A", "client_B"]:
    folder_path = os.path.join(base_path, folder)
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Charger le texte
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
        
        for doc in docs:
            # AJOUT CRITIQUE DE LA METADONNÉE TENANT
            doc.metadata = {"tenant": folder, "source": filename}
            documents_to_insert.append(doc)
            print(f"Préparation : {filename} (Client: {folder})")

# Envoi vers Supabase
if documents_to_insert:
    print("Envoi vers Supabase en cours...")
    vector_store = SupabaseVectorStore.from_documents(
        documents=documents_to_insert,
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents"
    )
    print("Terminé ! Données ingérées.")