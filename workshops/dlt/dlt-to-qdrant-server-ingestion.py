# zoomcamp_loader.py

import dlt
import requests
from dlt.destinations.adapters import qdrant_adapter

def zoomcamp_data():
    docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
    docs_response = requests.get(docs_url)
    documents_raw = docs_response.json()

    for course in documents_raw:
        course_name = course['course']
        for i, doc in enumerate(course['documents']):
            doc['course'] = course_name
            doc['id'] = f"{course_name}-{i}"
            yield doc

if __name__ == "__main__":
    data = list(zoomcamp_data())

    pipeline = dlt.pipeline(
        pipeline_name="zoomcamp_pipeline",
        destination="qdrant",
        dataset_name="zoomcamp_tagged_data"
    )

    load_info = pipeline.run(
        qdrant_adapter(
            data,
            embed=["text", "question"]
        ),
        write_disposition="replace"
    )

    print(pipeline.last_trace)