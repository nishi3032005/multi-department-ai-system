import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# -----------------------------
# LOAD PDF
# -----------------------------

loader = PyPDFLoader("data/NovaTech_Corporate_policy.pdf")
documents = loader.load()

print(f"Loaded {len(documents)} pages from PDF.")

full_text = "\n".join([doc.page_content for doc in documents])

# -----------------------------
# SECTION SPLITTING
# -----------------------------

sections = re.split(r"\n\d+\.\s", full_text)

docs = []

for section in sections:
    text = section.strip()
    if len(text) < 50:
        continue

    # Detect department based on keywords
    if "leave" in text.lower() or "recruit" in text.lower():
        department = "HR"
    elif "pricing" in text.lower() or "plan" in text.lower():
        department = "Sales"
    elif "invoice" in text.lower() or "payment" in text.lower():
        department = "Finance"
    else:
        department = "General"

    docs.append(
        Document(
            page_content=text,
            metadata={"department": department}
        )
    )

print(f"Split into {len(docs)} section chunks with metadata.")

# -----------------------------
# EMBEDDINGS
# -----------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(docs, embeddings)

vectorstore.save_local("faiss_metadata")

print("FAISS index with metadata created successfully.")
