"""
LOADER 2 — PyMuPDFLoader

Faster and better at preserving layout than PyPDF.
Uses the MuPDF engine under the hood.
Known to be great for invoices and structured documents.

Install:
    pip install pymupdf langchain-community
"""

from langchain_community.document_loaders import PyMuPDFLoader


# PICK ONE PDF TO TEST


PDF_PATH = "invoices/hilton_20230829.pdf"


# LOAD THE PDF


print("=" * 60)
print("  LOADER 2 — PyMuPDFLoader")
print("=" * 60)

loader = PyMuPDFLoader(PDF_PATH)
docs = loader.load()


# BASIC INFO


print(f"\nFile        : {PDF_PATH}")
print(f"Pages found : {len(docs)}")


# SHOW EXTRACTED TEXT PAGE BY PAGE


for i, doc in enumerate(docs):
    print(f"\n--- Page {i + 1} ---")
    print(doc.page_content)
