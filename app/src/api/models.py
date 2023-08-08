from pydantic import BaseModel
from typing import List


class EmbedQuestionResponse(BaseModel):
    embedded_question: List[float]


class Resource(BaseModel):
    summary: str
    episode_name: str
    segment_title: str
    url: str
    topic: str


class ResourceResponse(BaseModel):
    resources: List[Resource]


class AnswerResponse(BaseModel):
    answer: str
    resources: List[Resource]
