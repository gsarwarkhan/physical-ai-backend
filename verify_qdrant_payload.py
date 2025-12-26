import os
from qdrant_client import QdrantClient

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "https://44f1eced-a617-4726-8d5d-90f66a56e2e2.us-east4-0.gcp.cloud.qdrant.io")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XLi_uw9vKDmaR7DK565IDF7Ryl5AxubOMhVO2Mi928U")
COLLECTION_NAME = "humanoid_textbook"

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Test query
query_text = "What is ROS 2?"

print(f"Querying collection '{COLLECTION_NAME}' with text: '{query_text}'")

try:
    # Use the new query API which handles embedding automatically
    results = client.query(
        collection_name=COLLECTION_NAME,
        query_text=query_text,
        limit=1
    )
    
    print(f"Found {len(results)} results.")
    
    if results:
        # In the new Qdrant API, results might be a list of QueryResponse or ScoredPoint
        # Let's inspect the first result
        first = results[0]
        # Depending on version, it might be an object with .metadata or .payload
        # The 'add' method with FastEmbed usually stores text in 'document' field in metadata (or similar),
        # or 'text' payload.
        print("\n--- First Result ---")
        print(first)
        
        # Access payload/metadata safely
        payload = getattr(first, 'metadata', None) or getattr(first, 'payload', None)
        print(f"\nPayload/Metadata: {payload}")
        
    else:
        print("No results found. Indexing might have failed or is empty.")

except Exception as e:
    print(f"Error during query: {e}")
