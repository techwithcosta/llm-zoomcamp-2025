#%%
# Question 1. dlt version (1 point)

# !pip install -q "dlt[qdrant]" "qdrant-client[fastembed]"
import dlt
print(dlt.__version__)
#%%
# Question 2. Number of inserted rows (1 point)

import requests

# Step 1: Create DLT resource
@dlt.resource(write_disposition="replace", name="zoomcamp_data")
def zoomcamp_data():
    docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
    docs_response = requests.get(docs_url)
    documents_raw = docs_response.json()

    for course in documents_raw:
        course_name = course['course']

        for doc in course['documents']:
            doc['course'] = course_name
            yield doc

# Step 2: Define the destination
from dlt.destinations import qdrant

qd_path = "db.qdrant"

qdrant_destination = qdrant(
  qd_path=qd_path, 
)

# Step 3: Create and run the pipeline

dataset_name = "zoomcamp_tagged_data"

pipeline = dlt.pipeline(
    pipeline_name="zoomcamp_pipeline",
    destination=qdrant_destination,
    dataset_name=dataset_name
)
load_info = pipeline.run(zoomcamp_data())
print(pipeline.last_trace)
#%%
# Question 3. Embedding model (1 point)

collection_name = f"{dataset_name}_zoomcamp_data"

import json
with open(f'{qd_path}/meta.json', 'r') as file:
    data = json.load(file)

print(list(data["collections"][collection_name]["vectors"].keys())[0])
# %%
from qdrant_client import QdrantClient

# 1. Connect to local Qdrant
client = QdrantClient(path="db.qdrant")  # path to your local DB
#%%
# Check if vectors have been generated
points = client.scroll(
    collection_name=collection_name,
    limit=5,
    with_payload=True,
    with_vectors=True
)

for p in points[0]:
    print(p.vector)
# %%
