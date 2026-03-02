"""
LOADER 4 — PDFMinerLoader
PDFMiner is great at preserving text layout and spacing.
It handles complex PDFs better than PyPDF.
Good for documents with mixed columns and formatting.

Install:
    pip install pdfminer.six langchain-community
"""

from langchain_community.document_loaders import PDFMinerLoader


# PICK ONE PDF TO TEST


PDF_PATH = "invoices/europcar_20231009.pdf"


# LOAD THE PDF


print("=" * 60)
print("  LOADER 4 — PDFMinerLoader")
print("=" * 60)

loader = PDFMinerLoader(PDF_PATH)
docs = loader.load()


# BASIC INFO


print(f"\nFile        : {PDF_PATH}")
print(f"Pages found : {len(docs)}")


# SHOW EXTRACTED TEXT PAGE BY PAGE


for i, doc in enumerate(docs):
    print(f"\n--- Page {i + 1} ---")
    print(doc.page_content)
