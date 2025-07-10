#%%
from qdrant_client import QdrantClient, models

client = QdrantClient("http://localhost:6333")
collection_name = "zoomcamp_tagged_data_content"
model_handle = "BAAI/bge-small-en"

query = "I just discovered the course. Can I join now?"

def search(query, limit=1):

    results = client.query_points(
        collection_name=collection_name,
        query=models.Document( #embed the query text locally with "BAAI/bge-small-en"
            text=query,
            model=model_handle 
        ),
        using='fast-bge-small-en',
        limit=limit, # top closest matches
        with_payload=True # to get metadata in the results
    )

    return results

for i in search(query, limit=1).points[0]:
    print(i)