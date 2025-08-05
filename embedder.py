import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from utils.text_splitter import split_text

def load_text_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def embed_chunks(chunks, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, convert_to_tensor=False, show_progress_bar=True)
    return embeddings

def save_faiss_index(embeddings, chunks, index_path="data/faiss_index"):
    # FAISS index
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Simpan index dan mapping chunks
    faiss.write_index(index, f"{index_path}.index")
    with open(f"{index_path}_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print(f"[DONE] Index and chunks saved to {index_path}")
    return 1

if __name__ == "__main__":
    filename = "data/scraped_content.txt"
    text = load_text_file(filename)
    
    chunks = split_text(text, chunk_size=500)

    embeddings = embed_chunks(chunks)
    save_faiss_index(embeddings, chunks)
