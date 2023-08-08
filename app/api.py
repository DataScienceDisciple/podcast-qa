import os
import vecs

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Header
from mangum import Mangum

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.src.llm.qa.postgres_qa_engine import PostgresQAEngine, EmbeddingModel
from app.src.db.util import create_question_instance, add_recommended_resources, add_answer
from app.src.db.models import ResourcesHubermanLab

from app.src.api.models import ResourceResponse, AnswerResponse, EmbedQuestionResponse

load_dotenv()

DB_CONNECTION = f"postgresql://postgres:{os.environ['POSTGRES_DB_PASS']}@{os.environ['POSTGRES_DB_HOST']}:5432/postgres"
engine = create_engine(DB_CONNECTION)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
handler = Mangum(app)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine(db: Session = Depends(get_db)):

    embedding_model = EmbeddingModel("sbert")

    # create vector store client
    vx = vecs.create_client(DB_CONNECTION)
    qa_engine = PostgresQAEngine(embedding_model=embedding_model,
                                 sql_session=db,
                                 vecs_client=vx,
                                 vecs_collection_name="docs")
    return qa_engine


@app.get("/")
def hello():
    return {"message": "hello"}


@app.post("/embed_question", response_model=EmbedQuestionResponse)
def embed_question(question: str, engine: PostgresQAEngine = Depends(get_engine)) -> EmbedQuestionResponse:
    return EmbedQuestionResponse(embedded_question=engine.embed_question(question))


@app.post("/hubermanlab/answer", response_model=AnswerResponse)
def answer_hubermanlab(user_id: int, question: str, api_key: str = Header(...), engine: PostgresQAEngine = Depends(get_engine)) -> AnswerResponse:

    os.environ["OPENAI_API_KEY"] = api_key

    # Create a new question instance
    question_id = create_question_instance(
        engine.session, user_id, question, "answer")

    # Encoding question to embedding space
    embedded_question = engine.embed_question(question)

    # Finding relevant segments
    indices = engine.search_segments(embedded_question, 20)

    # Create new recommended resource instances and add them to the session
    add_recommended_resources(engine.session, question_id, indices)

    # Getting answers from segments
    relevant_summaries, n_relevant, n_non_relevant = engine.process_found_segments(
        question, indices)

    # Getting the final answer
    answer = engine.get_final_answer(question, relevant_summaries)

    # Adding the answer to the AnswersHubermanLab table
    add_answer(engine.session, user_id, question_id,
               answer, n_relevant, n_non_relevant)

    resources = [{"summary": value["summary"], "episode_name": value["episode_name"],
                  "segment_title": value["segment_title"], "url": value["url"], "topic": value["topic"]} for value in relevant_summaries.values()]

    return AnswerResponse(answer=answer, resources=resources)


@app.post("/hubermanlab/resource", response_model=ResourceResponse)
def resource_hubermanlab(user_id: int, question: str, engine: PostgresQAEngine = Depends(get_engine)) -> ResourceResponse:
    """
    Returns resources that are most relevant to a given question.
    """
    # Create a new question instance
    question_id = create_question_instance(
        engine.session, user_id, question, "resources")

    # Encoding question to embedding space
    embedded_question = engine.embed_question(question)

    # Finding relevant segments
    indices = engine.search_segments(embedded_question, 7)

    # Create new recommended resource instances and add them to the session
    add_recommended_resources(engine.session, question_id, indices)

    resources = []
    for ind in indices:
        resource = engine.session.query(ResourcesHubermanLab).get(ind)
        resources.append({"summary": resource.summary, "episode_name": resource.episode_name,
                         "segment_title": resource.segment_title, "url": resource.url, "topic": resource.topic})
    return ResourceResponse(resources=resources)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
