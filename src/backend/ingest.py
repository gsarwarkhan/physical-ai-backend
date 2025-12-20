import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from openai import OpenAI

# Configuration
QDRANT_URL = "YOUR_QDRANT_URL"
QDRANT_KEY = "YOUR_QDRANT_API_KEY"
OPENAI_KEY = "YOUR_OPENAI_API_KEY"
DOCS_PATH = "../docs" # Path to your Docusaurus docs folder

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
openai = OpenAI(api_key=OPENAI_KEY)

def prepare_collection():
    # Create collection if it doesn't exist
    client.recreate_collection(
        collection_name="humanoid_textbook",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )

def ingest_docs():
    points = []
    idx = 1
    for root, dirs, files in os.walk(DOCS_PATH):
        for filename in files:
            if filename.endswith(".md") or filename.endswith(".mdx"):
                with open(os.path.join(root, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Create vector embedding
                    vector = openai.embeddings.create(
                        input=content, 
                        model="text-embedding-3-small"
                    ).data[0].embedding
                    
                    points.append(PointStruct(
                        id=idx, 
                        vector=vector, 
                        payload={"text": content, "source": filename}
                    ))
                    idx += 1
    
    client.upsert(collection_name="humanoid_textbook", points=points)
    print(f"Successfully indexed {idx-1} documents.")

if __name__ == "__main__":
    prepare_collection()
    ingest_docs()