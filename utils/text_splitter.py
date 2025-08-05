import re

def split_text(text, chunk_size=500):
    # Bagi teks jadi kalimat
    sentences = re.split(r'(?<=[.?!]) +', text)
    
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) <= chunk_size:
            chunk += sentence + " "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + " "
    if chunk:
        chunks.append(chunk.strip())

    return chunks