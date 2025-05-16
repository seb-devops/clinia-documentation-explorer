import asyncio

import streamlit as st

from src.clinia_doc_agent import CliniaDocAgentsDeps, clinia_docs_agent
from src.utils import get_clients

st.set_page_config(page_title="Clinia Doc Chat", layout="centered")
st.title("💬 Clinia Documentation Chat")

if "history" not in st.session_state:
    st.session_state["history"] = []

query = st.text_input("Ask your question about Clinia documentation:", "")

submit = st.button("Send")

async def ask_agent(query):
    embedding_client, supabase = get_clients()
    deps = CliniaDocAgentsDeps(supabase=supabase, embedding_client=embedding_client)
    response = await clinia_docs_agent.run(query, deps=deps)
    return response.data

if submit and query:
    st.session_state["history"].append(("user", query))
    with st.spinner("The agent is thinking..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            answer = loop.run_until_complete(ask_agent(query))
        finally:
            loop.close()
    st.session_state["history"].append(("agent", answer))

for role, msg in st.session_state["history"]:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Clinia Agent:** {msg}")
