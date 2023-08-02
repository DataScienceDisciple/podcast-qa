import streamlit as st
import argparse
import os

from dotenv import load_dotenv, set_key
from loguru import logger
from pathlib import Path
import pandas as pd

from src.constants import (
    DF_SUMMARY_PATH,
    OPENAI_FAISS_INDEX,
    QA_OUTPUT_DIR,
    IMAGES_DIR,
    SBERT_FAISS_INDEX
)
from src.llm.qa.qa_engine import QAEngine, EmbeddingModel

qa_output_path = Path(os.getenv('QA_OUTPUT_DIR', QA_OUTPUT_DIR))
images_output_path = Path(os.getenv('IMAGES_DIR', IMAGES_DIR))

embedding_model = EmbeddingModel("sbert")
index_path = SBERT_FAISS_INDEX if embedding_model == EmbeddingModel.SBERT else OPENAI_FAISS_INDEX
qa_engine = QAEngine(embedding_model=embedding_model,
                     df_summary_path=DF_SUMMARY_PATH,
                     index_path=index_path,
                     qa_output_path=qa_output_path,
                     images_output_path=images_output_path,
                     # n_search=args.n_search,
                     # n_relevant_segments=args.n_relevant_segments,
                     # llm_model=args.llm_model,
                     # temperature=args.temperature
                     )
df_summary = pd.read_csv(DF_SUMMARY_PATH)

# Load environment variables from .env file


def on_api_key_change():
    os.environ['OPENAI_API_KEY'] = st.session_state.get('api_key')


def ui_spacer(n=2, line=False, next_n=0):
    for _ in range(n):
        st.write('')
    if line:
        st.tabs([' '])
    for _ in range(next_n):
        st.write('')


def api_key_panel():
    st.write("## Enter your OpenAI API key")
    st.text_input("OpenAI API key", type="password", key="api_key",
                  on_change=on_api_key_change, label_visibility="collapsed")


def main_layout():
    st.title("Podcast QA AI Engine")

    st.header("Ask question and get resources")
    input_text = st.text_area(label="",
                              placeholder="Your question", key="user_input")

    run_button = st.button("Run")

    if input_text and run_button:
        st.write("Your question is being processed. It can take a while.")
        st.write(input_text)

        answer, html = qa_engine.qa_full_flow(input_text)

        st.markdown(html, unsafe_allow_html=True)


# UI

st.set_page_config(page_title="Podcast QA AI Engine", page_icon=":robot")
with st.sidebar:
    with st.expander('Configure OpenAI API key'):
        api_key_panel()

main_layout()
