import os
import chromadb
from chromadb.utils import embedding_functions
from ingest import get_all_chunks

# The specific embedding model instructed: all-MiniLM-L6-v2
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "asu_cs_guide"

def setup_chromadb():
    """
    Initialize ChromaDB client and create/get the collection with our embedding model.
    """
    # Persistent client so we don't have to re-embed on every run
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    
    # SentenceTransformer wrapper provided by Chroma
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    
    # Create or get the collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn
    )
    
    return collection

def embed_and_store_chunks(collection, chunks):
    """
    Takes the chunks from ingest.py, formats them for ChromaDB, and adds them.
    """
    ids = []
    documents = []
    metadatas = []
    
    for c in chunks:
        # Create a unique ID for each chunk based on source and index
        chunk_id = f"{c['source']}_chunk_{c['chunk_index']}"
        ids.append(chunk_id)
        documents.append(c['text'])
        
        # Metadata must be simple types (strings, ints, floats, bools)
        metadatas.append({
            "source": c['source'],
            "chunk_index": c['chunk_index']
        })
        
    # Chroma handles the embedding automatically under the hood via the embedding_function
    print(f"Adding {len(documents)} chunks to ChromaDB...")
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    print("Done adding chunks.")

def retrieve(collection, query, top_k=4):
    """
    Retrieve the most relevant chunks for a given query.
    Returns the documents, metadata, and distances.
    """
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results

def main():
    # 1. Get all chunks from our ingestion script
    chunks = get_all_chunks(print_sample=False)
    
    # 2. Setup ChromaDB and Collection
    collection = setup_chromadb()
    
    # 3. Embed and store
    embed_and_store_chunks(collection, chunks)
    
    # 4. Test Retrieval with 3 Evaluation Questions
    test_queries = [
        "What do students say about the workload and projects for CSE 340, and what is the best way to manage it?",
        "What programming language is used in CSE 310, and what specific concepts should I be comfortable with before taking it?",
        "What is the general student consensus on Professor Ryan Meuth, and what external resource of his is highly recommended?"
    ]
    
    print("\n" + "="*50)
    print("TESTING RETRIEVAL")
    print("="*50)
    
    for q in test_queries:
        print(f"\nQUERY: '{q}'")
        results = retrieve(collection, q, top_k=3)
        
        # Results is a dictionary with lists of lists. We only queried 1 text, so we access index 0.
        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        
        for i in range(len(documents)):
            print(f"\n  [Result {i+1}] Distance: {distances[i]:.4f} | Source: {metadatas[i]['source']}")
            print(f"  Content: {documents[i]}")

if __name__ == "__main__":
    main()
