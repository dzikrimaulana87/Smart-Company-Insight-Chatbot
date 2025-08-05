from llama_cpp import Llama

llm = Llama(
    model_path="models/llama-2-7b-chat.Q4_K_S.gguf",
    n_ctx=2048,
    n_threads=6
)

def ask_local_llm(prompt):
    output = llm(
        prompt=prompt,
        max_tokens=400,
        temperature=0.3,
        stop=["User:", "Assistant:"]
    )
    return output["choices"][0]["text"].strip()
