"""
LOADER 1 — PyPDFLoader
The most basic and commonly used PDF loader in LangChain.
Let's see how well it extracts our invoice PDFs.

Install:
    pip install pypdf langchain-community
"""

from langchain_community.document_loaders import PyPDFLoader


# PICK ONE PDF TO TEST


PDF_PATH = "invoices/motelone_20230120.pdf"


# LOAD THE PDF


print("=" * 60)
print("  LOADER 1 — PyPDFLoader")
print("=" * 60)

loader = PyPDFLoader(PDF_PATH)
docs = loader.load()


# BASIC INFO


print(f"\nFile        : {PDF_PATH}")
print(f"Pages found : {len(docs)}")


# SHOW EXTRACTED TEXT PAGE BY PAGE


for i, doc in enumerate(docs):
    print(f"\n Page {i + 1} ")
    print(doc.page_content)
