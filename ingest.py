import os
import random
import glob

def clean_text(text):
    """
    Remove basic boilerplate, extra whitespace, or HTML artifacts if any.
    Since our documents are clean .txt files, we just normalize whitespace.
    """
    # Replace multiple spaces/newlines with a single space or normalized newline
    text = " ".join(text.split())
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=100):
    """
    Split text into chunks of `chunk_size` characters with `overlap` characters,
    respecting word boundaries so we don't cut words in half.
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        
        # Try to find a space to break at if we aren't at the end
        if end < text_len:
            last_space = text.rfind(' ', start, end)
            if last_space != -1 and last_space > start:
                end = last_space
                
        chunk = text[start:end].strip()
        if len(chunk) > 0:
            chunks.append(chunk)
            
        if end >= text_len:
            break
            
        # Calculate next start position based on overlap
        start = end - overlap
        
        # Adjust start forward to the next space to avoid starting mid-word
        if start > 0 and start < text_len:
            next_space = text.find(' ', start)
            if next_space != -1:
                start = next_space + 1

    return chunks

def main():
    docs_dir = "documents"
    txt_files = glob.glob(os.path.join(docs_dir, "*.txt"))
    
    all_chunks = []
    
    for filepath in txt_files:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        cleaned_text = clean_text(raw_text)
        
        # We specify 500 characters with 100 character overlap
        doc_chunks = chunk_text(cleaned_text, chunk_size=500, overlap=100)
        
        for i, c in enumerate(doc_chunks):
            # Keep track of metadata
            all_chunks.append({
                "source": os.path.basename(filepath),
                "chunk_index": i,
                "text": c
            })
            
    print(f"Total chunks created: {len(all_chunks)}")
    
    if len(all_chunks) > 0:
        print("\n--- 5 Random Chunks for Inspection ---")
        sample_chunks = random.sample(all_chunks, min(5, len(all_chunks)))
        for i, chunk in enumerate(sample_chunks):
            print(f"\n[Chunk {i+1} from {chunk['source']} - Length: {len(chunk['text'])} chars]")
            print(f"Text: {chunk['text']}")

if __name__ == "__main__":
    main()
