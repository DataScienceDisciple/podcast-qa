from pathlib import Path

DF_SUMMARY_PATH = Path('.') / 'data' / \
    'summary_kmeans_with_chatgpt_and_keywords_final.csv'

SBERT_FAISS_INDEX = Path('.') / 'data' / \
    'embeddings' / 'faiss_summary_index_sbert.faiss'
OPENAI_FAISS_INDEX = Path('.') / 'data' / \
    'embeddings' / 'faiss_summary_index.faiss'

SBERT_SUMMARY_EMBEDDINGS = Path(
    '.') / 'data' / 'embeddings' / 'summary_embeddings_sbert.joblib'
OPENAI_SUMMARY_EMBEDDINGS = Path(
    '.') / 'data' / 'embeddings' / 'summary_embeddings.joblib'

QA_OUTPUT_DIR = Path('.') / 'data' / 'qa-outputs'
IMAGES_DIR = Path('.') / 'data' / 'images'
