import os
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from supabase.client import create_client
import google.generativeai as genai

load_dotenv()

app = FastAPI()

# Configuration
API_KEYS = {
    "tenantA_key": "client_A",
    "tenantB_key": "client_B"
}

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
llm = genai.GenerativeModel('gemini-2.5-flash')

# Modèles de données
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

# Sécurité : Vérifie la clé API et retourne le Tenant ID
async def get_tenant_id(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Clé API invalide")
    return API_KEYS[x_api_key]

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Backend is running"}

@app.get("/models")
async def list_models():
    """List available Gemini models"""
    models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            models.append(m.name)
    return {"models": models}

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest, tenant_id: str = Depends(get_tenant_id)):
    
    try:
        # 1. Get query embedding
        query_embedding = embeddings.embed_query(request.query)
        
        # 2. Use direct Supabase RPC call with tenant filter (fix for langchain filter bug)
        try:
            response = supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "tenant_filter": tenant_id,
                    "match_count": 3
                }
            ).execute()
            
            if not response.data:
                return QueryResponse(answer="Aucune info trouvée.", sources=[])
            
            # Convert results to langchain Documents
            results = []
            for row in response.data:
                doc = Document(
                    page_content=row.get("content", ""),
                    metadata=row.get("metadata", {})
                )
                results.append(doc)
                
        except Exception as e:
            print(f"RPC call failed: {e}")
            # Fallback: Use direct Supabase query (bypasses langchain bug)
            try:
                response = supabase.table("documents").select("content, metadata").execute()
                if not response.data:
                    return QueryResponse(answer="Aucune info trouvée.", sources=[])
                
                # Filter by tenant
                tenant_docs = [doc for doc in response.data if doc.get("metadata", {}).get("tenant") == tenant_id]
                
                if not tenant_docs:
                    return QueryResponse(answer="Aucune info trouvée.", sources=[])
                
                results = []
                for doc in tenant_docs[:3]:
                    results.append(Document(
                        page_content=doc.get("content", ""),
                        metadata=doc.get("metadata", {})
                    ))
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                return QueryResponse(answer="Erreur lors de la recherche.", sources=[])
        
        if not results:
            return QueryResponse(answer="Aucune info trouvée.", sources=[])

        # 3. Prepare context for Gemini
        context_text = "\n\n".join([doc.page_content for doc in results])
        sources = list(set([doc.metadata.get("source") for doc in results]))
        
        # 4. Generate response
        prompt = f"""
Tu es un assistant pro. Réponds à la question en utilisant UNIQUEMENT le contexte ci-dessous.
Si la réponse n'est pas dans le contexte, dis "Je ne sais pas".

Contexte: {context_text}
Question: {request.query}
"""
        
        response = llm.generate_content(prompt)
        answer = response.text
        
        return QueryResponse(answer=answer, sources=sources)
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
