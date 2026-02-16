#  Multi-Department AI System (Prompt-Orchestrated Multi-Agent Architecture)

##  Project Overview

This project implements a **multi-department AI system** using:

-  Groq LLM (LLaMA 3.1)
- LangChain (LCEL - Modern Syntax)
-  Prompt Engineering
-  Role-based Department Isolation
-  Multi-department Response Merging

The system simulates an IT company with multiple departments such as:

- HR
- Engineering
- Sales
- Finance
- Support

It intelligently routes user queries to the correct department(s) and merges responses when necessary.

---

##  Architecture
User Query
↓
LLM Router (JSON classification)
↓
Department Chains (Role-based prompts)
↓
Refusal Validation
↓
Merge Layer (if multiple departments)
↓
Final Unified Response


##  How It Works

1 Router Layer
An LLM-based router classifies user queries into department(s) using structured JSON output.

Example:
```json
{"departments": ["Sales", "Finance"]}

2 Department Layer

Each department is implemented as an isolated role-based prompt with strict scope enforcement.

If a query does not belong to a department, it responds with:

This query does not fall under my department.

3 Validation Layer

If:

Router returns empty list → clarification requested

Any department refuses → clarification requested

4 merge layer

If multiple departments respond, a senior manager prompt merges responses into a single professional output.


## Installation & Setup

1  Clone Repository
git clone <your-repo-url>
cd multi_department_ai


2 Create Virtual Environment
python -m venv venv

Activate:
Windows:
venv\Scripts\activate
Mac/Linux:
source venv/bin/activate

3 Install Dependencies
pip install -r requirements.txt

4 Add Groq API Key
Create a .env file:

GROQ_API_KEY=your_groq_api_key_here

5 Run Application
python main.py


6 Example Queries

### Sales Queries
- What pricing plans do you offer?
- Do you provide enterprise packages?
- Can you share a quotation for your AI solution?

### Finance Queries
- What are your payment terms?
- How is the invoice generated?
- When are invoices issued?

### HR Queries
- How can I apply for leave?
- What is the salary processing cycle?
- What employee benefits are offered?

### Engineering Queries
- We are facing a deployment issue in production.
- What architecture does your platform use?
- Is your API REST-based?

### Support Queries
- I cannot log into my account.
- How do I reset my password?
- The dashboard is not loading properly.

---

## Combined / Multi-Department Queries

The system also supports queries that belong to multiple departments.  
It routes the query to all relevant departments and merges their responses into a single unified answer.

### Examples:

- Client wants pricing and invoice details.
- Please provide pricing structure along with payment terms.
- We need a proposal including pricing model and billing process.
- Explain your enterprise package and invoice generation workflow.
- Share quotation details and outline your payment schedule.
