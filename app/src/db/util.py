import datetime
from sqlalchemy.orm import Session

from .models import QuestionsHubermanLab, RecommendedResourcesHubermanLab, AnswersHubermanLab


def create_question_instance(db: Session, user_id: int, question: str, mode: str):
    new_question = QuestionsHubermanLab(
        user_id=user_id, created_at=datetime.datetime.now(), question=question, mode=mode)
    db.add(new_question)
    db.commit()
    return new_question.id


def add_recommended_resources(db: Session, question_id: int, indices: dict):
    for resource_id, similarity_score in indices.items():
        new_recommended_resource = RecommendedResourcesHubermanLab(
            question_id=question_id, resource_id=resource_id, similarity_score=similarity_score)
        db.add(new_recommended_resource)
    db.commit()


def add_answer(db: Session, user_id: int, question_id: int, answer: str, n_relevant: int, n_non_relevant: int):
    new_answer = AnswersHubermanLab(
        user_id=user_id, question_id=question_id, answer=answer, n_relevant=n_relevant, n_non_relevant=n_non_relevant)
    db.add(new_answer)
    db.commit()
