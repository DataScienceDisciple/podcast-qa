import os
import requests
from .models import AnswerResponse, EmbedQuestionResponse, ResourceResponse
from dotenv import load_dotenv
from typing import Union

load_dotenv()


def call_embed_question(question: str) -> Union[EmbedQuestionResponse, None]:
    ENDPOINT = "embed_question"
    url = f"{os.environ['LAMBDA_FUNCTION_URL']}{ENDPOINT}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "question": question
    }

    response = requests.post(url, params=data, headers=headers)

    if response.status_code == 200:
        return EmbedQuestionResponse(**response.json())
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


def call_answer_hubermanlab(user_id: int, question: str, api_key: str) -> Union[AnswerResponse, None]:
    ENDPOINT = "hubermanlab/answer"
    url = f"{os.environ['LAMBDA_FUNCTION_URL']}{ENDPOINT}"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    data = {
        "user_id": user_id,
        "question": question
    }

    response = requests.post(url, params=data, headers=headers)

    if response.status_code == 200:
        return AnswerResponse(**response.json())
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


def call_resource_hubermanlab(user_id: int, question: str) -> Union[ResourceResponse, None]:
    ENDPOINT = "hubermanlab/resource"
    url = f"{os.environ['LAMBDA_FUNCTION_URL']}{ENDPOINT}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "user_id": user_id,
        "question": question
    }

    response = requests.post(url, params=data, headers=headers)

    if response.status_code == 200:
        return ResourceResponse(**response.json())
    else:
        print(f"Request failed with status code {response.status_code}")
        return None
