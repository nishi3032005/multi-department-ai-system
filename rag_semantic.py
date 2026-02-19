import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# -----------------------------
# LOAD PDF
# -----------------------------

loader = PyPDFLoader("data/NovaTech_Corporate_policy.pdf")
documents = loader.load()

print(f"Loaded {len(documents)} pages from PDF.")

# -----------------------------
# EMBEDDINGS MODEL
# -----------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# SEMANTIC CHUNKING
# -----------------------------

semantic_splitter = SemanticChunker(embeddings)

docs = semantic_splitter.split_documents(documents)

print(f"Split into {len(docs)} semantic chunks.")

# -----------------------------
# CREATE FAISS INDEX
# -----------------------------

vectorstore = FAISS.from_documents(docs, embeddings)

vectorstore.save_local("faiss_semantic")

print("Semantic FAISS index created successfully.")
