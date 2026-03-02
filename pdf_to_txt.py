"""
PDF to TXT Converter

Converts each invoice PDF into a clean TXT file.
Uses PDFPlumber (our best loader) to preserve structure.
Saves each invoice as a separate TXT file.

"""

import os
import pdfplumber

# 
# CONFIGURATION
# 

INPUT_FOLDER  = "invoices"       # folder with PDF files
OUTPUT_FOLDER = "invoices_txt"   # folder to save TXT files

# 
# CREATE OUTPUT FOLDER IF NOT EXISTS
# 

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 
# GET ALL PDF FILES
# 

pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".pdf")]

if not pdf_files:
    print("No PDF files found in invoices/ folder.")
    exit()

print(f"Found {len(pdf_files)} PDF files.")
print("Starting conversion...\n")

# 
# CONVERT EACH PDF TO TXT
# 

success = 0
failed  = 0

for filename in sorted(pdf_files):

    pdf_path = os.path.join(INPUT_FOLDER, filename)
    txt_name = filename.replace(".pdf", ".txt")
    txt_path = os.path.join(OUTPUT_FOLDER, txt_name)

    try:
        with pdfplumber.open(pdf_path) as pdf:

            with open(txt_path, "w", encoding="utf-8") as txt_file:

                # Write file header
                txt_file.write("=" * 60 + "\n")
                txt_file.write(f"  INVOICE: {filename}\n")
                txt_file.write("=" * 60 + "\n\n")

                # Extract text page by page
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()

                    if text:
                        txt_file.write(f"--- Page {i + 1} ---\n")
                        txt_file.write(text.strip())
                        txt_file.write("\n\n")
                        txt_file.write("-" * 60 + "\n\n")

                # Write file footer
                txt_file.write("=" * 60 + "\n")
                txt_file.write("  END OF INVOICE\n")
                txt_file.write("=" * 60 + "\n")

        print(f"  {filename}  →  {txt_name}")
        success += 1

    except Exception as e:
        print(f"  {filename}  →  ERROR: {e}")
        failed += 1

# 
# SUMMARY
# 

print("\n" + "=" * 60)
print("  CONVERSION COMPLETE")
print("=" * 60)
print(f"  Successfully converted : {success}")
print(f"  Failed                 : {failed}")
print(f"  TXT files saved in     : {OUTPUT_FOLDER}/")
print("=" * 60)