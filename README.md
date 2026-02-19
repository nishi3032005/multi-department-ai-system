# Multi-Department AI System

**Prompt-Orchestrated Multi-Agent Architecture with FastAPI**

A smart AI system that routes user queries to the correct department, retrieves relevant company policy information, and returns a professional answer — all via a REST API.

---

## Tech Stack

- **LLM** — Groq (LLaMA 3.1 8B Instant)
- **Framework** — LangChain (LCEL)
- **Vector Store** — FAISS with metadata filtering
- **Embeddings** — HuggingFace `all-MiniLM-L6-v2`
- **API** — FastAPI + Uvicorn
- **Environment** — Python-dotenv

---

## Departments

- **HR** — Leave, Hiring, Payroll, Benefits
- **Engineering** — Architecture, Deployment, APIs
- **Sales** — Pricing, Packages, Proposals
- **Finance** — Invoices, Payment Terms, Billing
- **Support** — Login Issues, Tickets, Complaints

---

## Architecture

```
User Query
    ↓
FastAPI  →  /query endpoint
    ↓
LLM Router  →  classifies query into department(s)
    ↓
FAISS RAG  →  retrieves relevant chunks per department
    ↓
LLM  →  generates department answer
    ↓
Merge Layer  →  combines if multiple departments
    ↓
JSON Response
```

---

## How It Works

### Step 1 — Router
The LLM reads the query and returns a JSON list of relevant departments.

```json
{ "departments": ["Sales", "Finance"] }
```

If the router returns empty, it falls back to searching all departments.

### Step 2 — RAG Per Department
Each department:
- Filters FAISS using metadata `{"department": "Finance"}`
- Retrieves top 4 relevant chunks from the policy PDF
- Passes chunks as context to the LLM with a role-based prompt

If no documents are found, it returns:
```
The requested information is not available in company records.
```

### Step 3 — Merge
If multiple departments respond, a senior manager prompt merges all answers into one clean, professional response.

### Step 4 — FastAPI
The pipeline is exposed as a REST API with 4 endpoints:

```
GET   /         →  Welcome message
GET   /health   →  Server health check
POST  /query    →  Full pipeline (route + RAG + merge + answer)
POST  /route    →  Routing decision only (no RAG)
```

---

## Project Structure

```
multi_department_ai/
│
├── api.py                        # FastAPI application
├── main.py                       # Terminal-based pipeline
├── rag_setup.py                  # FAISS index builder with metadata
├── rag_section.py                # Section-based chunking (alternate)
├── rag_semantic.py               # Semantic chunking (alternate)
│
├── faiss_metadata/               # Saved FAISS vector index
│   ├── index.faiss
│   └── index.pkl
│
├── data/
│   └── NovaTech_Corporate_policy.pdf
│
├── .env                          # API keys (do not share or commit)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup & Installation

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd multi_department_ai
```

**2. Create and activate virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
pip install fastapi uvicorn
```

**4. Add your Groq API key**

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

**5. Build the FAISS index** (one-time setup)

```bash
python rag_setup.py
```

---

## Running the Application

**Option A — Terminal mode**

```bash
python main.py
```

**Option B — API mode**

```bash
uvicorn api:app --reload
```

Then open: `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

---

## API Example

**Request**

```bash
POST /query
Content-Type: application/json

{
  "query": "What are the payment terms?"
}
```

**Response**

```json
{
  "query": "What are the payment terms?",
  "departments_routed": ["Finance"],
  "answer": "The standard payment terms are Net 30, meaning payment is due 30 days from the invoice date. Custom contracts may define alternate schedules."
}
```

---

## Example Queries to Test

**Single department queries**

```
What pricing plans do you offer?          →  Sales
What are the payment terms?               →  Finance
How can I apply for leave?                →  HR
I cannot log into my account.             →  Support
What architecture does your platform use? →  Engineering
```

**Multi-department queries**

```
Please provide pricing structure along with payment terms.
We need a proposal including pricing model and billing process.
Explain your enterprise package and invoice generation workflow.
```

---

## Chunking Strategy

The corporate policy PDF is processed using **Section-Based Chunking**:

- The full PDF text is split using a regex pattern on numbered sections (`1.`, `2.`, `3.` ...)
- Each chunk is tagged with a department label based on keyword matching
- These metadata labels enable filtered retrieval per department at query time

```python
sections = re.split(r"\n\d+\.\s", full_text)

Document(
    page_content=text,
    metadata={"department": "Finance"}
)
```

---

## Important Notes

- Never commit your `.env` file — add it to `.gitignore`
- Run `rag_setup.py` once before starting the API to build the FAISS index
- The `faiss_metadata/` folder must exist before running `api.py` or `main.py`
