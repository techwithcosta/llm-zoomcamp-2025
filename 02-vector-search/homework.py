#%%
# Question 1. Embedding the query (1 point)

# !pip install fastembed
from fastembed import TextEmbedding

model = TextEmbedding(model_name="jinaai/jina-embeddings-v2-small-en")

query = "I just discovered the course. Can I join now?"
embeddings = list(model.embed(query))
q = embeddings[0]
print(min(q))
# %%
# Question 2. Cosine similarity with another vector (1 point)

doc = 'Can I still join the course after the start date?'
embeddings = list(model.embed(doc))
d = embeddings[0]
print(q.dot(d))
# %%
# Question 3. Ranking by cosine (1 point)

import numpy as np

documents = [{'text': "Yes, even if you don't register, you're still eligible to submit the homeworks.\nBe aware, however, that there will be deadlines for turning in the final projects. So don't leave everything for the last minute.",
  'section': 'General course-related questions',
  'question': 'Course - Can I still join the course after the start date?',
  'course': 'data-engineering-zoomcamp'},
 {'text': 'Yes, we will keep all the materials after the course finishes, so you can follow the course at your own pace after it finishes.\nYou can also continue looking at the homeworks and continue preparing for the next cohort. I guess you can also start working on your final capstone project.',
  'section': 'General course-related questions',
  'question': 'Course - Can I follow the course after it finishes?',
  'course': 'data-engineering-zoomcamp'},
 {'text': "The purpose of this document is to capture frequently asked technical questions\nThe exact day and hour of the course will be 15th Jan 2024 at 17h00. The course will start with the first  “Office Hours'' live.1\nSubscribe to course public Google Calendar (it works from Desktop only).\nRegister before the course starts using this link.\nJoin the course Telegram channel with announcements.\nDon’t forget to register in DataTalks.Club's Slack and join the channel.",
  'section': 'General course-related questions',
  'question': 'Course - When will the course start?',
  'course': 'data-engineering-zoomcamp'},
 {'text': 'You can start by installing and setting up all the dependencies and requirements:\nGoogle cloud account\nGoogle Cloud SDK\nPython 3 (installed with Anaconda)\nTerraform\nGit\nLook over the prerequisites and syllabus to see if you are comfortable with these subjects.',
  'section': 'General course-related questions',
  'question': 'Course - What can I do before the course starts?',
  'course': 'data-engineering-zoomcamp'},
 {'text': 'Star the repo! Share it with friends if you find it useful ❣️\nCreate a PR if you see you can improve the text or the structure of the repository.',
  'section': 'General course-related questions',
  'question': 'How can we contribute to the course?',
  'course': 'data-engineering-zoomcamp'}]

texts = [doc["text"] for doc in documents]
embeddings = list(model.embed(texts))

V = np.array(embeddings)

similarities = V.dot(q)

best_i = np.argmax(similarities)
print("Highest similarity document index:", best_i)
# %%
# Question 4. Ranking by cosine, version two (1 point)

texts = [doc['question'] + ' ' + doc['text'] for doc in documents]
embeddings = list(model.embed(texts))

V = np.array(embeddings)

similarities = V.dot(q)

best_i = np.argmax(similarities)
print("Highest similarity document index:", best_i)
# %%
# Question 5. Selecting the embedding model (1 point)

from fastembed import TextEmbedding
supported_models = TextEmbedding.list_supported_models()
texts = [model['dim'] for model in supported_models]
min(texts)
# %%
# Question 6. Indexing with qdrant (2 points)

import os

script_dir = os.path.dirname(os.path.realpath(__file__))
print(script_dir)

# !sudo docker pull qdrant/qdrant
# !sudo docker run -p 6333:6333 -p 6334:6334 \
#    -v "$(pwd)/02-vector-search/qdrant_storage:/qdrant/storage:z" \
#    qdrant/qdrant

# !pip install qdrant-client

import requests
from qdrant_client import QdrantClient, models

client = QdrantClient("http://localhost:6333")

docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

documents = []

for course in documents_raw:
    course_name = course['course']
    if course_name != 'machine-learning-zoomcamp':
        continue

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)

texts = [doc['question'] + ' ' + doc['text'] for doc in documents]
texts

# Create a Collection
model_handle = "BAAI/bge-small-en"

for model in supported_models:
    if model['model'] == model_handle:
        EMBEDDING_DIMENSIONALITY = model['dim']

# Define the collection name
collection_name = "zoomcamp-rag"

# Create the collection with specified vector parameters
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=EMBEDDING_DIMENSIONALITY,  # Dimensionality of the vectors
        distance=models.Distance.COSINE  # Distance metric for similarity search
    )
)

# Create, Embed & Insert Points into the Collection
points = []
id = 0

for course in documents_raw:
    for doc in course['documents']:

        point = models.PointStruct(
            id=id,
            vector=models.Document(text=doc['text'], model=model_handle), #embed text locally with "jinaai/jina-embeddings-v2-small-en" from FastEmbed
            payload={
                "text": doc['text'],
                "section": doc['section'],
                "course": course['course']
            } #save all needed metadata fields
        )
        points.append(point)

        id += 1

client.upsert(
    collection_name=collection_name,
    points=points
)

# Create a Collection (homework)
model_handle = "BAAI/bge-small-en"

for model in supported_models:
    if model['model'] == model_handle:
        EMBEDDING_DIMENSIONALITY = model['dim']

# Define the collection name
collection_name = "zoomcamp-rag-homework"

# Create the collection with specified vector parameters
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=EMBEDDING_DIMENSIONALITY,  # Dimensionality of the vectors
        distance=models.Distance.COSINE  # Distance metric for similarity search
    )
)

# Create, Embed & Insert Points into the Collection
points = []
id = 0

for course in documents_raw:
    course_name = course['course']
    if course_name != 'machine-learning-zoomcamp':
        continue

    for doc in course['documents']:

        point = models.PointStruct(
            id=id,
            vector=models.Document(text=doc['question'] + ' ' + doc['text'], model=model_handle), #embed text locally with "jinaai/jina-embeddings-v2-small-en" from FastEmbed
            payload={
                "text": doc['question'] + ' ' + doc['text'],
            } #save all needed metadata fields
        )
        points.append(point)

        id += 1

client.upsert(
    collection_name=collection_name,
    points=points
)

def search(query, limit=1):

    results = client.query_points(
        collection_name=collection_name,
        query=models.Document( #embed the query text locally with "BAAI/bge-small-en"
            text=query,
            model=model_handle 
        ),
        limit=limit, # top closest matches
        with_payload=True #to get metadata in the results
    )

    return results

search(query, limit=1).points[0].score
# %%
# http://localhost:6333/dashboard#/collections/zoomcamp-rag/visualize

{
  "limit": 948,
  "color_by": {
    "payload": "course"
  }
}

# RUN