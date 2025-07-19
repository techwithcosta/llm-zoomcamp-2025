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
# Question 4. MRR Qdrant (1 point)
# %%
# Question 5. Average cosine (1 point)
# %%
# Question 6. Average Rouge-1 F1 (1 point)
