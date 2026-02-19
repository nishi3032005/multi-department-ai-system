import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

loader = PyPDFLoader("data/NovaTech_Corporate_policy.pdf")
documents = loader.load()

full_text = "\n".join([doc.page_content for doc in documents])

sections = re.split(r"\n\d+\.\s", full_text)

docs = []

for section in sections:
    text = section.strip()
    if len(text) < 50:
        continue

    text_lower = text.lower()

    if "leave" in text_lower or "recruit" in text_lower:
        department = "HR"
    elif "pricing" in text_lower or "plan" in text_lower:
        department = "Sales"
    elif "invoice" in text_lower or "payment" in text_lower:
        department = "Finance"
    elif "login" in text_lower or "ticket" in text_lower:
        department = "Support"
    else:
        department = "Engineering"

    docs.append(
        Document(
            page_content=text,
            metadata={"department": department}
        )
    )

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("faiss_metadata")

print("Final metadata-based FAISS index created successfully.")
