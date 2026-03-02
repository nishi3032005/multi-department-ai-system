"""
LOADER 3 — PDFPlumberLoader
Best loader for PDFs that have TABLES.
It extracts table rows and columns more accurately.
Great for invoices that have itemized billing tables.

Install:
    pip install pdfplumber langchain-community
"""

from langchain_community.document_loaders import PDFPlumberLoader


# PICK ONE PDF TO TEST


PDF_PATH = "data/NovaTech_Corporate_policy.pdf"


# LOAD THE PDF


print("=" * 60)
print("  LOADER 3 — PDFPlumberLoader")
print("=" * 60)

loader = PDFPlumberLoader(PDF_PATH)
docs = loader.load()


# BASIC INFO


print(f"\nFile        : {PDF_PATH}")
print(f"Pages found : {len(docs)}")


# SHOW EXTRACTED TEXT PAGE BY PAGE


for i, doc in enumerate(docs):
    print(f"\n--- Page {i + 1} ---")
    print(doc.page_content)