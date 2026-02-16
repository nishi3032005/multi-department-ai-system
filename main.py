import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

# ==================================================
# INITIALIZE LLM
# ==================================================

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0  # deterministic routing
)

# ==================================================
# CONSTANTS
# ==================================================

REFUSAL_MESSAGE = "This query does not fall under my department."

# ==================================================
# ROUTER LAYER
# ==================================================

router_prompt = ChatPromptTemplate.from_template("""
You are an internal routing system for an IT company.

Available Departments:

HR:
- Hiring, interviews
- Leave requests
- Payroll and salary
- Employee benefits
- Internal policies

Engineering:
- Code issues
- Bugs
- System architecture
- Deployment
- Infrastructure
- APIs and technical stack

Sales:
- Pricing
- Product packages
- Business proposals
- Client onboarding offers
- High-level billing explanation
- Pricing structure discussion

Finance:
- Invoice generation
- Payment terms
- Budget
- Revenue
- Cost breakdown
- Billing details

Support:
- Customer complaints
- Account problems
- Login issues
- Usage guidance
- Feature confusion

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

# ==================================================
# DEPARTMENT LAYER
# ==================================================

hr_prompt = ChatPromptTemplate.from_template("""
You are the HR Department of an IT company.

Your responsibilities:
- Hiring and interviews
- Leave requests
- Payroll and salary
- Employee benefits
- Internal policies

Rules:
1. Only answer questions within your responsibilities.
2. If outside your scope, respond exactly with:
   "This query does not fall under my department."
3. Be professional and concise.
4. Do not mention other departments.

User Query:
{query}
""")

engineering_prompt = ChatPromptTemplate.from_template("""
You are the Engineering Department of an IT company.

Your responsibilities:
- Code issues
- Bugs
- System architecture
- Deployment
- Infrastructure
- APIs and technical stack

Rules:
1. Only answer technical questions.
2. If outside your scope, respond exactly with:
   "This query does not fall under my department."
3. Be precise and technical.
4. Do not mention other departments.

User Query:
{query}
""")

sales_prompt = ChatPromptTemplate.from_template("""
You are the Sales Department of an IT company.

Your responsibilities:
- Pricing
- Product packages
- Business proposals
- Client onboarding offers
- High-level billing explanation
- Pricing structure discussion

Rules:
1. Only answer sales-related questions.
2. If outside your scope, respond exactly with:
   "This query does not fall under my department."
3. Maintain a professional tone.
4. Do not mention other departments.

User Query:
{query}
""")

finance_prompt = ChatPromptTemplate.from_template("""
You are the Finance Department of an IT company.

Your responsibilities:
- Invoice generation
- Payment terms
- Budget
- Revenue
- Cost breakdown
- Billing details

Rules:
1. Only answer financial questions.
2. If outside your scope, respond exactly with:
   "This query does not fall under my department."
3. Be clear and factual.
4. Do not mention other departments.

User Query:
{query}
""")

support_prompt = ChatPromptTemplate.from_template("""
You are the Customer Support Department of an IT company.

Your responsibilities:
- Customer complaints
- Account issues
- Login problems
- Usage guidance
- Feature confusion

Rules:
1. Only assist with customer-related issues.
2. If outside your scope, respond exactly with:
   "This query does not fall under my department."
3. Be polite and helpful.
4. Do not mention other departments.

User Query:
{query}
""")

# Convert prompts to chains
hr_chain = hr_prompt | llm
engineering_chain = engineering_prompt | llm
sales_chain = sales_prompt | llm
finance_chain = finance_prompt | llm
support_chain = support_prompt | llm

department_map = {
    "HR": hr_chain,
    "Engineering": engineering_chain,
    "Sales": sales_chain,
    "Finance": finance_chain,
    "Support": support_chain
}


def execute_departments(departments, user_query):
    responses = []

    for dept in departments:
        if dept in department_map:
            response = department_map[dept].invoke({"query": user_query})
            responses.append(response.content.strip())

    return responses

# ==================================================
# MERGE LAYER
# ==================================================

merge_prompt = ChatPromptTemplate.from_template("""
You are a senior manager of the company.

Combine the following department responses into ONE clear,
professional, and non-repetitive final answer.

Do not mention departments.
Ensure logical flow.
Remove redundancy.

Responses:
{responses}
""")

merge_chain = merge_prompt | llm


def contains_refusal(responses):
    for r in responses:
        if r.strip() == REFUSAL_MESSAGE:
            return True
    return False

# ==================================================
# FINAL ORCHESTRATION LOOP
# ==================================================

if __name__ == "__main__":
    while True:
        user_input = input("\nEnter query (type 'exit' to stop): ")

        if user_input.lower() == "exit":
            break

        # Step 1: Routing
        departments = route_query(user_input)

        if not departments:
            print("\nCould you clarify whether this relates to HR, Engineering, Sales, Finance, or Support?")
            continue

        # Step 2: Department Execution
        responses = execute_departments(departments, user_input)

        # Step 3: Refusal Validation
        if contains_refusal(responses):
            print("\nCould you clarify your query? It appears ambiguous across departments.")
            continue

        # Step 4: Merge if Multiple Departments
        if len(responses) > 1:
            merged_response = merge_chain.invoke({
                "responses": "\n\n".join(responses)
            })
            print("\nFinal Response:\n")
            print(merged_response.content.strip())
        else:
            print("\nFinal Response:\n")
            print(responses[0])
