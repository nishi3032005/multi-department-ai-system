"""
PDF to DOCX Converter
Converts each invoice PDF into a Word DOCX file.
Preserves structure, tables, spacing, and layout.
Uses pdf2docx library which gives best results.

"""

import os
from pdf2docx import Converter


# CONFIGURATION


INPUT_FOLDER  = "invoices"        # folder with PDF files
OUTPUT_FOLDER = "invoices_docx"   # folder to save DOCX files


# CREATE OUTPUT FOLDER IF NOT EXISTS


os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# GET ALL PDF FILES


pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".pdf")]

if not pdf_files:
    print("No PDF files found in invoices/ folder.")
    exit()

print(f"Found {len(pdf_files)} PDF files.")
print("Starting conversion...\n")


# CONVERT EACH PDF TO DOCX


success = 0
failed  = 0

for filename in sorted(pdf_files):

    pdf_path  = os.path.join(INPUT_FOLDER, filename)
    docx_name = filename.replace(".pdf", ".docx")
    docx_path = os.path.join(OUTPUT_FOLDER, docx_name)

    try:
        # Convert PDF to DOCX
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        print(f"✅  {filename}  →  {docx_name}")
        success += 1

    except Exception as e:
        print(f"❌  {filename}  →  ERROR: {e}")
        failed += 1


# SUMMARY


print("\n" + "=" * 60)
print("  CONVERSION COMPLETE")
print("=" * 60)
print(f"  Successfully converted : {success}")
print(f"  Failed                 : {failed}")
print(f"  DOCX files saved in    : {OUTPUT_FOLDER}/")
print("=" * 60)
print("""
Next step:
  Open any DOCX file in Word or VS Code
  Check if structure matches the original PDF
  Tables, spacing, and layout should be preserved!
""")