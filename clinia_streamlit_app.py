import asyncio

import streamlit as st

from src.clinia_doc_agent import CliniaDocAgentsDeps, clinia_docs_agent
from src.utils import get_clients

st.set_page_config(page_title="Clinia Doc Chat", layout="centered")
st.title("💬 Clinia Documentation Chat")

if "history" not in st.session_state:
    st.session_state["history"] = []

query = st.text_input("Pose ta question sur la documentation Clinia :", "")

submit = st.button("Envoyer")

async def ask_agent(query):
    embedding_client, supabase = get_clients()
    deps = CliniaDocAgentsDeps(supabase=supabase, embedding_client=embedding_client)
    response = await clinia_docs_agent.run(query, deps=deps)
    return response.data

if submit and query:
    st.session_state["history"].append(("user", query))
    with st.spinner("L'agent réfléchit..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            answer = loop.run_until_complete(ask_agent(query))
        finally:
            loop.close()
    st.session_state["history"].append(("agent", answer))

for role, msg in st.session_state["history"]:
    if role == "user":
        st.markdown(f"**Vous :** {msg}")
    else:
        st.markdown(f"**Agent Clinia :** {msg}")
