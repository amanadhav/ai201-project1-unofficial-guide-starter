import os
import gradio as gr
from groq import Groq
from dotenv import load_dotenv

from retrieve import setup_chromadb, retrieve

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY in .env file")

groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize vector DB collection once at startup
collection = setup_chromadb()

def ask(question: str):
    # Retrieve top 3 relevant chunks
    results = retrieve(collection, question, top_k=3)
    
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    
    # If no documents are found, fast fail
    if not documents:
        return {
            "answer": "I don't have enough information on that.",
            "sources": []
        }
        
    # Build context and unique sources list
    context_parts = []
    unique_sources = set()
    for doc, meta in zip(documents, metadatas):
        context_parts.append(f"Content:\n{doc}\nSource: {meta['source']}")
        unique_sources.add(meta['source'])
        
    context_str = "\n\n".join(context_parts)
    
    # Strict Grounding Prompt
    system_prompt = """
    You are an ASU Computer Science course and professor guide assistant.
    You must answer the user's question using ONLY the provided context.
    If the provided context does not contain the answer, you must say exactly: "I don't have enough information on that."
    Do not use outside knowledge. Do not guess.
    If you use the information, briefly cite the source in your text, for example: (source: filename.txt).
    """
    
    user_prompt = f"Context:\n{context_str}\n\nQuestion: {question}"
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        max_tokens=512,
    )
    
    answer = response.choices[0].message.content.strip()
    
    return {
        "answer": answer,
        "sources": list(unique_sources)
    }

def handle_query(question):
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    if not sources:
        sources = "No sources retrieved."
    return result["answer"], sources

# Gradio Interface
with gr.Blocks(title="The Unofficial Guide - ASU CS Courses & Professors") as demo:
    gr.Markdown("# The Unofficial Guide - ASU CS Courses & Professors")
    gr.Markdown("Ask a question about ASU Computer Science courses (like CSE 340, CSE 310) or professors (like Ryan Meuth, Mutsumi Nakamura).")
    
    inp = gr.Textbox(label="Your question", placeholder="e.g. What do students say about Professor Ryan Meuth?")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
