from fastapi import APIRouter, Depends
from routers.authentication import get_current_user
from fastapi_service import models
from module import generate_embedding, pinecone_queries, generate_answer
import pinecone

router = APIRouter(tags=["dummy"])
# pinecone_api_key = "6e0b7ddc-cec5-4df7-b06f-78a30dde865a"

# pinecone.deinit()
# Initialize Pinecone with your API key
# pinecone.init(api_key=pinecone_api_key)

# index = pinecone.Index(index_name="damg7245-qabot")


@router.post("/ask")
async def ask_question(
    question: models.Question, user: dict = Depends(get_current_user)
):
    embedding = generate_embedding.generate_embedding(question.question)
    top_k = 2  # You can adjust this value based on your requirements

    pinecone_results = pinecone_queries.query_pinecone(
        embedding, top_k, selected_pdfs=question.pdfs
    )

    print(pinecone_results)
    query = pinecone_queries.format_query(
        question.question, pinecone_results["matches"]
    )
    print(query)

    answer = generate_answer.generate_answer(query)

    return {"answer": answer}