from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    name = Column(String)

    questions = relationship("QuestionsHubermanLab", backref="user")
    answers = relationship("AnswersHubermanLab", backref="user")


class QuestionsHubermanLab(Base):
    __tablename__ = 'questions_hubermanlab'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    question = Column(String)
    mode = Column(String)

    answers = relationship("AnswersHubermanLab", backref="question")
    recommended_resources = relationship(
        "RecommendedResourcesHubermanLab", backref="question")


class AnswersHubermanLab(Base):
    __tablename__ = 'answers_hubermanlab'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions_hubermanlab.id'))
    answer = Column(String)
    n_relevant = Column(Integer)
    n_non_relevant = Column(Integer)


class ResourcesHubermanLab(Base):
    __tablename__ = 'resources_hubermanlab'

    id = Column(Integer, primary_key=True)
    summary = Column(String)
    episode_name = Column(String)
    segment_title = Column(String)
    url = Column(String)
    topic = Column(String)

    recommended_resources = relationship(
        "RecommendedResourcesHubermanLab", backref="resource")


class RecommendedResourcesHubermanLab(Base):
    __tablename__ = 'recommended_resources_hubermanlab'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions_hubermanlab.id'))
    resource_id = Column(Integer, ForeignKey('resources_hubermanlab.id'))
    similarity_score = Column(Float)
