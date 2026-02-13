import streamlit as st
import requests

st.title("Test Technique SaaS - Multi-Tenant")

# Sidebar pour simuler la connexion
with st.sidebar:
    api_key = st.text_input("Entrez votre API KEY", type="password")
    if api_key == "tenantA_key":
        st.success("Connecté : Client A")
    elif api_key == "tenantB_key":
        st.info("Connecté : Client B")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    if not api_key:
        st.error("Il faut une API Key !")
    else:
        try:
            # Appel au Backend FastAPI
            res = requests.post(
                "http://127.0.0.1:8000/chat",
                headers={"X-API-KEY": api_key},
                json={"query": prompt}
            )
            
            if res.status_code == 200:
                data = res.json()
                reply = f"{data['answer']}\n\n*Sources: {data['sources']}*"
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.chat_message("assistant").write(reply)
            else:
                st.error(f"Erreur API: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Le backend n'est pas lancé ou erreur: {str(e)}")
