import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# ──────────────────────────────────────────
# LOAD ENV
# ──────────────────────────────────────────

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")


# ──────────────────────────────────────────
# FASTAPI APP
# ──────────────────────────────────────────

app = FastAPI(
    title="NovaTech Multi-Department AI API",
    description="AI-powered query routing across HR, Engineering, Sales, Finance, and Support departments.",
    version="1.0.0"
)


# ──────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ──────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    departments_routed: list[str]
    answer: str


# ──────────────────────────────────────────
# LLM INIT
# ──────────────────────────────────────────

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0
)


# ──────────────────────────────────────────
# VECTOR STORE
# ──────────────────────────────────────────

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "faiss_metadata",
    embeddings,
    allow_dangerous_deserialization=True
)


# ──────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────

router_prompt = ChatPromptTemplate.from_template("""
You are an internal routing system for NovaTech Solutions Pvt. Ltd.

Available Departments:

HR:
- Hiring, Leave policy, Payroll, Employee benefits, Internal policies

Engineering:
- System architecture, Deployment, APIs, Technical stack, Infrastructure

Sales:
- Pricing plans, Product packages, Enterprise proposals, Discounts

Finance:
- Invoice process, Payment terms, Billing, Refund policy

Support:
- Login issues, Account recovery, Ticket process, Customer complaints

Rules:
1. Return ONLY valid JSON.
2. Do NOT explain reasoning.
3. Do NOT answer the user.
4. If unclear, return: {{"departments": []}}

Output format:
{{
  "departments": ["DepartmentName"]
}}

User Query:
{query}
""")

router_chain = router_prompt | llm


def route_query(user_query: str) -> list[str]:
    response = router_chain.invoke({"query": user_query})
    raw_output = response.content.strip()
    try:
        parsed = json.loads(raw_output)
        return parsed.get("departments", [])
    except json.JSONDecodeError:
        return []


# ──────────────────────────────────────────
# RAG EXECUTION
# ──────────────────────────────────────────

def execute_departments(departments: list[str], user_query: str) -> list[str]:
    responses = []

    for dept in departments:
        retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 4,
                "filter": {"department": dept}
            }
        )

        retrieved_docs = retriever.invoke(user_query)

        if not retrieved_docs:
            responses.append(
                "The requested information is not available in company records."
            )
            continue

        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        rag_prompt = f"""
You are the {dept} Department of NovaTech Solutions Pvt. Ltd.

Use ONLY the company policy information below to answer.

If the answer is not present in the provided context, say:
"The requested information is not available in company records."

Company Policy Information:
{context}

User Query:
{user_query}
"""
        result = llm.invoke(rag_prompt)
        responses.append(result.content.strip())

    return responses


# ──────────────────────────────────────────
# MERGE LAYER
# ──────────────────────────────────────────

merge_prompt = ChatPromptTemplate.from_template("""
You are a senior manager at NovaTech Solutions Pvt. Ltd.

Combine the following department responses into ONE clear,
professional, and structured final answer.

Do not mention departments.
Ensure logical flow.
Remove repetition.
If all responses indicate information is unavailable,
return exactly:
"The requested information is not available in company records."

Responses:
{responses}
""")

merge_chain = merge_prompt | llm


# ──────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Welcome to NovaTech Multi-Department AI API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    user_query = request.query.strip()

    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Step 1: Route
    departments = route_query(user_query)

    # Fallback: search all departments
    if not departments:
        departments = ["HR", "Engineering", "Sales", "Finance", "Support"]

    # Step 2: RAG per department
    responses = execute_departments(departments, user_query)

    # Step 3: Merge if multiple
    if len(responses) > 1:
        merged = merge_chain.invoke({
            "responses": "\n\n".join(responses)
        })
        final_answer = merged.content.strip()
    else:
        final_answer = responses[0]

    return QueryResponse(
        query=user_query,
        departments_routed=departments,
        answer=final_answer
    )


@app.post("/route")
def route_only(request: QueryRequest):
    """Returns only the department routing decision without executing RAG."""
    user_query = request.query.strip()

    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    departments = route_query(user_query)

    return {
        "query": user_query,
        "departments": departments if departments else ["Fallback - All Departments"]
    }