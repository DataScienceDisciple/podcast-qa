import faiss
import json
import time
import numpy as np
import pandas as pd

from enum import Enum
from loguru import logger
from pathlib import Path

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from sentence_transformers import SentenceTransformer

from .prompts.segment_template import SEGMENT_SYSTEM_TEMPLATE, SEGMENT_HUMAN_TEMPLATE
from .prompts.final_answer_template import FINAL_ANSWER_SYSTEM_TEMPLATE, FINAL_ANSWER_HUMAN_TEMPLATE


class EmbeddingModel(Enum):
    SBERT = "sbert"
    OPENAI = "openai"


class QAEngine:
    def __init__(self,
                 embedding_model: EmbeddingModel,
                 df_summary_path: Path,
                 index_path: Path,
                 qa_output_path: Path,
                 images_output_path: Path,
                 n_search: int = 20,
                 n_relevant_segments: int = 3,
                 llm_model: str = 'gpt-3.5-turbo',
                 temperature: float = 0) -> None:

        if embedding_model.value == EmbeddingModel.SBERT.value:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_ndim = self.embedding_model.get_sentence_embedding_dimension()
        elif embedding_model.value == EmbeddingModel.OPENAI.value:
            self.embedding_model = OpenAIEmbeddings()
            self.embedding_ndim = 1536

        self.df_summary = pd.read_csv(df_summary_path)
        self.index = faiss.read_index(str(index_path))
        self.qa_output_path = qa_output_path
        self.images_output_path = images_output_path
        self.n_search = n_search
        self.n_relevant_segments = n_relevant_segments
        self.llm_model = llm_model
        self.temperature = temperature

    def segment_check_and_answer(self, question: str, context: str) -> str:
        chat = ChatOpenAI(temperature=self.temperature,
                          model_name=self.llm_model)

        system_message_prompt = SystemMessagePromptTemplate.from_template(
            SEGMENT_SYSTEM_TEMPLATE)
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            SEGMENT_HUMAN_TEMPLATE)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt])

        chain = LLMChain(llm=chat, prompt=chat_prompt)
        output = chain.run(question=question, context=context)

        return output

    def embed_question(self, question) -> np.array:
        if isinstance(self.embedding_model, SentenceTransformer):
            return np.array(self.embedding_model.encode(question)).reshape(1, self.embedding_ndim)

        elif isinstance(self.embedding_model, OpenAIEmbeddings):
            return np.array(self.embedding_model.embed_query(question)).reshape(1, self.embedding_ndim)

    def search_segments(self, embedded_question: np.array):
        similarity, indices = self.index.search(
            embedded_question, self.n_search)
        return similarity, indices

    def process_found_segments(self, question: str, indices: np.array):
        n_relevant_segments = 0
        relevant_summaries = {}
        non_relevant_summaries = {}

        for ind in indices[0]:
            if n_relevant_segments < self.n_relevant_segments:
                context = self.df_summary.loc[ind, "summary"]
                answer = self.segment_check_and_answer(
                    question=question, context=context)
                if answer.startswith("Not relevant"):
                    non_relevant_summaries[int(ind)] = answer
                else:
                    n_relevant_segments += 1
                    relevant_summaries[int(ind)] = {"answer": answer,
                                                    "URL": self.df_summary.loc[ind, "url"],
                                                    "keywords": self.df_summary.loc[ind, "keywords"]}
            else:
                return relevant_summaries, non_relevant_summaries
        return relevant_summaries, non_relevant_summaries

    def get_final_answer(self, question: str, answers: dict):
        chat = ChatOpenAI(temperature=self.temperature,
                          model_name=self.llm_model)

        system_message_prompt = SystemMessagePromptTemplate.from_template(
            FINAL_ANSWER_SYSTEM_TEMPLATE)
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            FINAL_ANSWER_HUMAN_TEMPLATE)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt])

        prompt_context = "\n".join(
            [f"ANSWER {i+1}:\n{answer['answer']}\n" for i, answer in enumerate(answers.values())])

        chain = LLMChain(llm=chat, prompt=chat_prompt)
        output = chain.run(question=question, context=prompt_context)

        output += "\n\nHere are HubermanLab Podcast segments that relate to your question:\n\n"
        for i, value in enumerate(answers.values()):
            output += f'{i+1}. {value["URL"]}\n'

        return output

    def qa_full_flow(self, question):
        start_time = time.time()

        # Encoding question to embedding space
        embedded_question = self.embed_question(question)

        # Finding relevant segments
        similarity, indices = self.search_segments(embedded_question)

        # Getting answers from segments
        relevant_segments, non_relevant_segments = self.process_found_segments(
            question, indices)

        relevant_path = self.qa_output_path / f"{question}-relevant.json"
        json.dump(relevant_segments, open(relevant_path, "w"))

        non_relevant_path = self.qa_output_path / \
            f"{question}-non-relevant.json"
        json.dump(non_relevant_segments, open(non_relevant_path, "w"))

        # Getting the final answer
        answer = self.get_final_answer(question, relevant_segments)

        final_answer_path = self.qa_output_path / \
            f"{question}-final-answer.txt"
        with open(final_answer_path, "w") as f:
            f.write(answer)
        end_time = time.time()

        logger.info(f"Full QA flow time: {round(end_time-start_time, 2)}")
        return answer