# %%
# !pip install -U minsearch qdrant_client ipywidgets
# %%
import requests
import pandas as pd

url_prefix = 'https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main/03-evaluation/'
docs_url = url_prefix + 'search_evaluation/documents-with-ids.json'
documents = requests.get(docs_url).json()

ground_truth_url = url_prefix + 'search_evaluation/ground-truth-data.csv'
df_ground_truth = pd.read_csv(ground_truth_url)
ground_truth = df_ground_truth.to_dict(orient='records')
# %%
from tqdm.auto import tqdm

def hit_rate(relevance_total):
    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt / len(relevance_total)

def mrr(relevance_total):
    total_score = 0.0

    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                total_score = total_score + 1 / (rank + 1)

    return total_score / len(relevance_total)

def evaluate(ground_truth, search_function):
    relevance_total = []

    for q in tqdm(ground_truth):
        doc_id = q['document']
        results = search_function(q)
        relevance = [d['id'] == doc_id for d in results]
        relevance_total.append(relevance)

    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total),
    }
# %%
# Question 1. Hitrate for minsearch text (1 point)

from minsearch import Index

# Create and fit the index
index = Index(
    text_fields=["question", "text", "section"],
    keyword_fields=["course", "id"]
)
index.fit(documents)

# Search with filters and boosts
def search_function(q):
    filter_dict = {"course": q['course']}
    # boost_dict = {'question': 3, 'section': 0.5} # returns {'hit_rate': 0.7722066133563864, 'mrr': 0.661454506159499}
    boost_dict = {'question': 1.5, 'section': 0.1}
    results = index.search(
        query=q['question'],
        filter_dict=filter_dict,
        boost_dict=boost_dict,
        num_results=5)
    return results

evaluate_results = evaluate(ground_truth=ground_truth, search_function=search_function)
print(evaluate_results['hit_rate'])
# %%
from minsearch import VectorSearch

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline

texts = []

for doc in documents:
    t = doc['question']
    texts.append(t)

pipeline = make_pipeline(
    TfidfVectorizer(min_df=3),
    TruncatedSVD(n_components=128, random_state=1)
)
X = pipeline.fit_transform(texts)
# %%
# Question 2. MRR Vector search (question field) (1 point)

vindex = VectorSearch(keyword_fields={'course'})
vindex.fit(X, documents)

# Search with a query vector and filters
def search_function(q):
    filter_dict = {"course": q['course']}
    query_vector = pipeline.transform([q['question']])[0] # convert text query to vector
    results = vindex.search(
        query_vector,
        filter_dict=filter_dict,
        num_results=5)
    return results

evaluate_results = evaluate(ground_truth=ground_truth, search_function=search_function)
print(evaluate_results['mrr'])
# %%
# Question 3. Hitrate Vector search (question + text fields) (1 point)

texts = []

for doc in documents:
    t = doc['question'] + ' ' + doc['text']
    texts.append(t)

X = pipeline.fit_transform(texts)

vindex = VectorSearch(keyword_fields={'course'})
vindex.fit(X, documents)

# Search with a query vector and filters
def search_function(q):
    filter_dict = {"course": q['course']}
    query_vector = pipeline.transform([q['question']])[0] # convert text query to vector
    results = vindex.search(
        query_vector,
        filter_dict=filter_dict,
        num_results=5)
    return results

evaluate_results = evaluate(ground_truth=ground_truth, search_function=search_function)
print(evaluate_results['hit_rate'])
# %%
# Run qdrant container

# !sudo docker run -p 6333:6333 -p 6334:6334 \
#    -v "$(pwd)/03-evaluation/qdrant_storage:/qdrant/storage:z" \
#    qdrant/qdrant
# %%
# Question 4. MRR Qdrant (1 point)

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

supported_models = TextEmbedding.list_supported_models()

model_handle = "jinaai/jina-embeddings-v2-small-en"
limit = 5

for model in supported_models:
    if model['model'] == model_handle:
        EMBEDDING_DIMENSIONALITY = model['dim']

# Define the collection name
collection_name = "zoomcamp-evaluation-homework"

# Create the collection with specified vector parameters
client = QdrantClient("http://localhost:6333")

client.recreate_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=EMBEDDING_DIMENSIONALITY,  # Dimensionality of the vectors
        distance=models.Distance.COSINE  # Distance metric for similarity search
    )
)

points = []
id = 0

for doc in documents:
    text = doc['question'] + ' ' + doc['text']
    point = models.PointStruct(
        id=id,
        vector=models.Document(text=text, model=model_handle),
        payload={
            "text": text,
            "section": doc['section'],
            "course": doc['course'],
            "id": doc['id']
        } #save all needed metadata fields
    )
    points.append(point)
    id += 1

client.upsert(
    collection_name=collection_name,
    points=points
)

# check collection at http://localhost:6333/dashboard

from qdrant_client.models import Filter, FieldCondition, MatchValue

# Search with filters
def search_function(q):
    results_tmp = client.query_points(
        collection_name=collection_name,
        query=models.Document(
            text=q['question'],
            model=model_handle
        ),
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="course",
                    match=MatchValue(value=q['course'])
                )
            ]
        ),
        limit=limit, # top closest matches
        with_payload=True #to get metadata in the results
    )
    results = []
    for r in results_tmp.points:
        results.append(r.payload)
    return results
evaluate_results = evaluate(ground_truth=ground_truth, search_function=search_function)
print(evaluate_results['mrr'])
# %%
# Question 5. Average cosine (1 point)

import numpy as np

def cosine(u, v):
    u_norm = np.sqrt(u.dot(u))
    v_norm = np.sqrt(v.dot(v))
    return u.dot(v) / (u_norm * v_norm)

results_url = url_prefix + 'rag_evaluation/data/results-gpt4o-mini.csv'
df_results = pd.read_csv(results_url)

pipeline = make_pipeline(
    TfidfVectorizer(min_df=3),
    TruncatedSVD(n_components=128, random_state=1)
)

pipeline.fit(df_results.answer_llm + ' ' + df_results.answer_orig + ' ' + df_results.question)

# Create empty list to store similarities
cosines = []

# Loop over all rows
for _, row in df_results.iterrows():
    # Get vector embeddings
    v_llm = pipeline.transform([row['answer_llm']])[0]
    v_orig = pipeline.transform([row['answer_orig']])[0]
    
    # Compute cosine similarity
    sim = cosine(v_llm, v_orig)
    cosines.append(sim)

average_cosine = np.mean(cosines)
print(average_cosine)
# %%
# Question 6. Average Rouge-1 F1 (1 point)

# !pip install rouge
from rouge import Rouge
rouge_scorer = Rouge()

r = df_results.iloc[10]
scores = rouge_scorer.get_scores(r.answer_llm, r.answer_orig)[0]

# Create empty list to store rouge scores
scores = []

# Loop over all rows
for _, row in df_results.iterrows():
    rouge_1_f1 = rouge_scorer.get_scores(row['answer_llm'], row['answer_orig'])[0]['rouge-1']['f']
    scores.append(rouge_1_f1)

average_scores = np.mean(scores)
print(float(np.mean(scores)))
# %%
