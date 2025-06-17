#%%
# !docker run -it \
#     --rm \
#     --name elasticsearch \
#     -m 4GB \
#     -p 9200:9200 \
#     -p 9300:9300 \
#     -e "discovery.type=single-node" \
#     -e "xpack.security.enabled=false" \
#     docker.elastic.co/elasticsearch/elasticsearch:9.0.2
#%%
# !pip install requests
# !pip install elasticsearch
#%%
# Question 1. Running Elastic (1 point)

import requests

response = requests.get('http://localhost:9200')
output = response.json()
print(output['version']['build_hash'])
# %%
# Question 2. Indexing the data (1 point)

docs_url = 'https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/refs/heads/main/01-intro/documents.json'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

documents = []

for course in documents_raw:
    course_name = course['course']

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)

from elasticsearch import Elasticsearch

es_client = Elasticsearch('http://localhost:9200')

index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"} 
        }
    }
}

index_name = "course-questions"

es_client.indices.create(index=index_name, body=index_settings)

from tqdm.auto import tqdm

for doc in tqdm(documents):
    es_client.index(index=index_name, document=doc)
# %%
# Question 3. Searching (1 point)

query = "How do execute a command on a Kubernetes pod?"

search_query = {
    "size": 1,
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": query,
                    "fields": ["question^4", "text"],
                    "type": "best_fields"
                }
            }
        }
    }
}
response = es_client.search(index=index_name, body=search_query)

for hit in response.body['hits']['hits']:
    print(hit['_score'])
# %%
# Question 4. Filtering (1 point)

query = "How do copy a file to a Docker container?"

search_query = {
    "size": 3,
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": query,
                    "fields": ["question"],
                    "type": "best_fields"
                }
            },
            "filter": {
                "term": {
                    "course": "machine-learning-zoomcamp"
                }
            }
        }
    }
}
response = es_client.search(index=index_name, body=search_query)

hits = []
for hit in response.body['hits']['hits']:
    question = hit['_source']['question']
    hits.append(question)
print(hits[2])
# %%
# Question 5. Building a prompt (1 point)

contexts = []

for hit in response.body['hits']['hits']:
    question = hit['_source']['question']
    text = hit['_source']['text']
    context_template = f"""
Q: {question}
A: {text}
""".strip()
    contexts.append(context_template)

context = "\n\n".join(contexts)

prompt_template = f"""
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {query}

CONTEXT:
{context}
""".strip()

print(len(prompt_template))
# %%
# !pip install tiktoken
#%%
# Question 6. Tokens (1 point)

import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o")
num_tokens = len(encoding.encode(prompt_template))
num_tokens
# %%
