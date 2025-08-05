import streamlit as st
import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
from llama_cpp import Llama
from models.local_llm import ask_local_llm
from scrapper import scrape_company_pages
from embedder import load_text_file, split_text, embed_chunks, save_faiss_index

# ==== SETUP ====
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(EMBED_MODEL_NAME)


# ==== UTIL ====
TEXT_FILE = "data/scraped_content.txt"
INDEX_FILE = "data/faiss_index.index"
CHUNK_FILE = "data/faiss_index_chunks.pkl"

def get_token_count(text):
    return len(text.split())

def build_prompt(context, query):
    return (
        f"You are a helpful assistant. Use the following company information to answer the question.\n\n"
        f"{context}\n\n"
        f"Question: {query}\nAnswer:"
    )

def search_similar_chunks(query, top_k=3):
    index = faiss.read_index(INDEX_FILE)
    with open(CHUNK_FILE, "rb") as f:
        chunks = pickle.load(f)
    query_embedding = model.encode([query])[0]
    D, I = index.search(np.array([query_embedding]), top_k)
    return [chunks[i] for i in I[0]]

def prepare_embedding_if_needed(company):
    scrape_company_pages(company)
    if not (os.path.exists(INDEX_FILE) and os.path.exists(CHUNK_FILE)):
        text = load_text_file(TEXT_FILE)
        chunks = split_text(text, chunk_size=500)
        embeddings = embed_chunks(chunks)
        save_faiss_index(embeddings, chunks)

# ==== UI COMPONENT ====

def show_company_details():
    if 'selected_company' in st.session_state:
        company = st.session_state['selected_company']

        st.subheader(f"Details for {company['Company']}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Industry:** {company.get('Industry', 'N/A')}")
            st.write(f"**Phone:** {company.get('Business_phone', 'N/A')}")
            st.write(f"**Website:** {company.get('Website', 'N/A')}")
        with col2:
            st.write(f"**Street:** {company.get('Street', 'N/A')}")
            st.write(f"**City:** {company.get('City', 'N/A')}")

        if st.button("Start chat about this company"):
            prepare_embedding_if_needed(company)
            st.session_state.chat_mode = True

        if st.button("← Back to Search Results"):
            del st.session_state['selected_company']
            st.switch_page("main.py")


def show_chat_interface():
    query = st.text_input("What do you want to ask?")
    if query:
        text = load_text_file(TEXT_FILE)
        token_count = get_token_count(text)
        # st.caption(f"📦 Context length: {token_count} words")

        if token_count < 700:
            # Direct stuffing
            prompt = build_prompt(text, query)
            answer = ask_local_llm(prompt)
            st.success("✅ Generating answer ...")
            st.write(answer)
        else:
            # Use FAISS
            chunks = search_similar_chunks(query)
            context = "\n\n".join(chunks)
            prompt = build_prompt(context, query)
            answer = ask_local_llm(prompt)
            st.success("✅ Generating answer ...")
            st.write(answer)

            with st.expander("🔍 Context used"):
                for i, chunk in enumerate(chunks):
                    st.markdown(f"**Chunk {i+1}:**\n{chunk}\n")

# ==== APP RUN ====

st.set_page_config(page_title="Company Chatbot (Fixed Files)", layout="wide")

if 'selected_company' in st.session_state:
    st.title("Company Details & Chat")
    if 'chat_mode' not in st.session_state or not st.session_state.chat_mode:
        show_company_details()
    else:
        if st.button("← Back to Company Info"):
            st.session_state.chat_mode = False
        show_chat_interface()
else:
    st.error("No company selected. Please go back to the search results.")
    if st.button("← Back to Search Results"):
        st.switch_page("main.py")
