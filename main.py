import argparse
import os

from dotenv import load_dotenv, set_key
from loguru import logger
from pathlib import Path
import pandas as pd

from app.src.constants import (
    DF_SUMMARY_PATH,
    OPENAI_FAISS_INDEX,
    QA_OUTPUT_DIR,
    IMAGES_DIR,
    SBERT_FAISS_INDEX
)
from app.src.llm.qa.local_qa_engine import QAEngine, EmbeddingModel

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is not set!")


def create_parser():
    parser = argparse.ArgumentParser(
        description='AI-powered podcast search and Q&A tool.')
    parser.add_argument('--set-env-var', nargs=2,
                        help='Set an environment variable and save it to .env file. Usage: --set-env-var VAR_NAME var_value')
    parser.add_argument('--set-output-paths', nargs=2,
                        help='Set output paths. Usage: --set-output-paths QA_OUTPUT_DIR IMAGES_DIR')
    parser.add_argument('-q', '--question', help='Ask a question.')
    parser.add_argument('-r', '--resources', help='Search resources.')
    parser.add_argument('--embedding_model', default='sbert', choices=[
                        'sbert', 'openai'], help='Choose the embedding model. Options: "sbert", "openai". Default: "sbert".')
    parser.add_argument('--n_search', type=int, default=20,
                        help='Number of segments to search for. Default: 20.')
    parser.add_argument('--n_relevant_segments', type=int,
                        default=3, help='Number of relevant segments. Default: 3.')
    parser.add_argument('--llm_model', default='gpt-3.5-turbo',
                        help='Language model to use. Default: "gpt-3.5-turbo".')
    parser.add_argument('--temperature', type=float, default=0,
                        help='Temperature for the model. Default: 0.')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.set_env_var:
        var_name, var_value = args.set_env_var

        # Write to .env file
        set_key('.env', var_name, var_value)

        # The environment variable is also set for the current process
        os.environ[var_name] = var_value

        print(f'Environment variable {var_name} set.')

    if args.set_output_paths:
        qa_output_path, images_output_path = map(Path, args.set_output_paths)
        set_key('.env', 'QA_OUTPUT_DIR', str(qa_output_path))
        set_key('.env', 'IMAGES_DIR', str(images_output_path))
        load_dotenv()  # Reload the environment variables

    qa_output_path = Path(os.getenv('QA_OUTPUT_DIR', QA_OUTPUT_DIR))
    images_output_path = Path(os.getenv('IMAGES_DIR', IMAGES_DIR))

    embedding_model = EmbeddingModel(args.embedding_model)
    index_path = SBERT_FAISS_INDEX if embedding_model == EmbeddingModel.SBERT else OPENAI_FAISS_INDEX

    qa_engine = QAEngine(embedding_model=embedding_model,
                         df_summary_path=DF_SUMMARY_PATH,
                         index_path=index_path,
                         qa_output_path=qa_output_path,
                         images_output_path=images_output_path,
                         n_search=args.n_search,
                         n_relevant_segments=args.n_relevant_segments,
                         llm_model=args.llm_model,
                         temperature=args.temperature)

    df_summary = pd.read_csv(DF_SUMMARY_PATH)

    if args.question:
        answer = qa_engine.qa_full_flow(args.question)
        print(
            f"Your question was answered and the answer is saved in {qa_output_path}")
        print(answer)

    if args.resources:
        embedded_question = qa_engine.embed_question(args.resources)
        similarity, indices = qa_engine.search_segments(embedded_question)

        relevant_segments = df_summary.iloc[indices[0]].copy()

        # Add the distances to the dataframe
        relevant_segments['similarity'] = similarity[0]

        relevant_segments = relevant_segments[[
            'episode_name', 'segment_name', 'summary', 'url', 'keywords', 'similarity']]

        # Sort by distances
        relevant_segments.sort_values(
            by='similarity', ascending=False, inplace=True)

        relevant_segments.to_csv(
            qa_output_path / 'relevant_segments.csv', index=False)
        print(
            f"Relevant segments were found and saved to {qa_output_path / 'relevant_segments.csv'}")
        print(relevant_segments.head())


if __name__ == '__main__':
    main()
