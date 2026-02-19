import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# LOAD ENVIRONMENT VARIABLES

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")



# INITIALIZE LLM


llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0
)



# LOAD FAISS VECTOR STORE


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "faiss_metadata",
    embeddings,
    allow_dangerous_deserialization=True
)


print("FAISS index loaded successfully.")



# ROUTER LAYER


router_prompt = ChatPromptTemplate.from_template("""
You are an internal routing system for NovaTech Solutions Pvt. Ltd.

Available Departments:

HR:
- Hiring
- Leave policy
- Payroll
- Employee benefits
- Internal policies

Engineering:
- System architecture
- Deployment
- APIs
- Technical stack
- Infrastructure

Sales:
- Pricing plans
- Product packages
- Enterprise proposals
- Discounts

Finance:
- Invoice process
- Payment terms
- Billing
- Refund policy

Support:
- Login issues
- Account recovery
- Ticket process
- Customer complaints

Rules:
1. Return ONLY valid JSON.
2. Do NOT explain reasoning.
3. Do NOT answer the user.
4. If unclear, return:
   {{"departments": []}}

Output format:
{{
  "departments": ["DepartmentName"]
}}

User Query:
{query}
""")

router_chain = router_prompt | llm


def route_query(user_query):
    response = router_chain.invoke({"query": user_query})
    raw_output = response.content.strip()

    try:
        parsed = json.loads(raw_output)
        return parsed.get("departments", [])
    except json.JSONDecodeError:
        return []



# RAG EXECUTION PER DEPARTMENT


def execute_departments(departments, user_query):
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



# MERGE LAYER


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



# MAIN LOOP


if __name__ == "__main__":
    while True:
        user_input = input("\nEnter query (type 'exit' to stop): ")

        if user_input.lower() == "exit":
            break

        # Step 1: Routing
        departments = route_query(user_input)

        # Router fallback (search all if unclear)
        if not departments:
            departments = ["HR", "Engineering", "Sales", "Finance", "Support"]

        # Step 2: Department RAG Execution
        responses = execute_departments(departments, user_input)

        # Step 3: Merge if Multiple Departments
        if len(responses) > 1:
            merged_response = merge_chain.invoke({
                "responses": "\n\n".join(responses)
            })
            print("\nFinal Response:\n")
            print(merged_response.content.strip())
        else:
            print("\nFinal Response:\n")
            print(responses[0])


            