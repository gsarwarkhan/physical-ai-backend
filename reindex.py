import os
import glob
from typing import List
from qdrant_client import QdrantClient

# Configuration
# Using the same Qdrant Cloud URL/Key as in the original code, or environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "https://44f1eced-a617-4726-8d5d-90f66a56e2e2.us-east4-0.gcp.cloud.qdrant.io")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XLi_uw9vKDmaR7DK565IDF7Ryl5AxubOMhVO2Mi928U")
COLLECTION_NAME = "humanoid_textbook"
DOCS_DIR = "docs"

# Initialize Qdrant Client
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def read_docs(directory: str) -> List[dict]:
    """
    Reads all .md and .mdx files from the given directory.
    Returns a list of dictionaries with 'text' and 'metadata'.
    """
    documents = []
    # Recursively find all markdown files
    files = glob.glob(os.path.join(directory, "**/*.md"), recursive=True) + \
            glob.glob(os.path.join(directory, "**/*.mdx"), recursive=True)
            
    print(f"Found {len(files)} documents to index.")
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Simple chunking logic (can be improved)
            # For now, we'll index the whole file or large chunks if they are too big?
            # Qdrant's FastEmbed handling will truncate if too long usually, 
            # but ideally we should chunk.
            # Let's do a simple split by headers or paragraphs if content is huge.
            # For this task, strict chunking might be overkill, but better safe.
            # Let's treat distinct sections as documents if possible, or just the file.
            # Given the constraints, let's stick to file-level or simple strict chunking.
            
            # Going with whole file content for now unless it's massive. 
            # If it's a textbook, chapters might be long. 
            # Let's simple chunk by double newline to avoid hitting token limits purely.
            
            chunks = content.split('\n\n')
            current_chunk = ""
            chunk_id = 0
            
            for part in chunks:
                if len(current_chunk) + len(part) < 1000: # Approx char limit per chunk
                    current_chunk += part + "\n\n"
                else:
                    if current_chunk.strip():
                        documents.append({
                            "text": current_chunk.strip(),
                            "metadata": {"source": file_path, "chunk_id": chunk_id}
                        })
                        chunk_id += 1
                    current_chunk = part + "\n\n"
            
            if current_chunk.strip():
                documents.append({
                    "text": current_chunk.strip(),
                    "metadata": {"source": file_path, "chunk_id": chunk_id}
                })
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    return documents

def reindex():
    print("Starting re-indexing process...")
    
    # 1. Delete existing collection if it exists
    if client.collection_exists(COLLECTION_NAME):
        print(f"Deleting existing collection '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)
    
    # 2. Recreate collection with correct parameters for FastEmbed
    # Qdrant `add` method automatically creates collection if not exists 
    # BUT we want to ensure it uses the correct vector params implicitly or explicitly.
    # Actually, `add` with `model` parameter handles schema creation automatically 
    # with the correct dimensions for that model.
    print(f"Creating/Updating collection '{COLLECTION_NAME}'...")
    
    docs = read_docs(DOCS_DIR)
    if not docs:
        print("No documents found. Aborting.")
        return

    documents_text = [d["text"] for d in docs]
    documents_metadata = [d["metadata"] for d in docs]
    
    # 3. Add documents using FastEmbed
    # This automatically models and embeds the documents.
    client.add(
        collection_name=COLLECTION_NAME,
        documents=documents_text,
        metadata=documents_metadata,
        batch_size=64,
        # Default model is 'BAAI/bge-small-en-v1.5' which is what we want (384 dim)
        # We can specify it explicitly to be safe.
    )
    
    print(f"Successfully indexed {len(documents_text)} chunks into '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    reindex()
