# 🧠 AI Company Insight Chatbot (Local LLM + Semantic Search)

This project is a chatbot powered by LLaMA 2 and semantic search using FAISS. It allows users to ask questions about specific companies based on scraped content from their official websites.

---

## 📌 Features

- ✅ Company-specific chatbot from scraped data
- ⚙️ Embedding via SentenceTransformer
- 🔍 Semantic search with FAISS
- 🤖 LLaMA 2 model served locally (`gguf`)
- 🧠 Automatic fallback to direct context if content is small
- 📦 Streamlit interface


## 📁 Project Structure

```
├── data/ # Data & embedding files
│ ├── scraped_content.txt # Text scraped from company website
│ ├── faiss_index.index # FAISS index file
│ └── faiss_index_chunks.pkl # Embedded chunks (raw texts)
│
├── models/
│ ├── llama-2-7b-chat.Q4_K_S.gguf # Local LLaMA model
│ └── local_llm.py # LLM interface setup
│
├── pages/
│ └── detail_data.py # Streamlit detail & chat UI
│
├── utils/
│ └── text_splitter.py # Text splitting utility
│
├── scrapper.py # Web content scraper
├── embedder.py # Embedding and FAISS indexer
├── main.py # Streamlit launcher
├── requirements.txt # Python dependencies
└── README.md # This file
```

---

## 🚀 How to Run

### 1. Clone & install dependencies
```bash
git clone https://github.com/yourname/company-insight-chatbot.git
cd company-insight-chatbot
pip install -r requirements.txt
```
### 2. Download LLaMA 2 gguf model
Place your model in 
```
models/llama-2-7b-chat.Q4_K_S.gguf
```

You can find it on [Hugging Face](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_S.gguf)

### 3. Launch the app
```
streamlit run main.py
```
## 💬 How It Works ###
Select a company

Click "Start Chat"

Scraper will extract website content (about, landing, etc.)

If content < 700 words → LLM uses direct prompt stuffing

If content ≥ 700 words → FAISS used to semantically search relevant chunks

LLaMA model answers your query strictly based on context

🔧 Requirements
All dependencies are listed in requirements.txt

## 📌 Future Improvements
- Add UI to select from multiple companies
- Add cache & history
- Deploy via Docker for reproducibility
- Using "smarter" llm
- More advanced scraping techniques

🧑‍💻 Author
@dzikrimaulana87