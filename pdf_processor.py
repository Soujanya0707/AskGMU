import os
import ocrmypdf
import pdfplumber

pdf_folder = "data/pdfs"
text_folder = "data/text"
ocr_folder = "data/ocr_pdfs"

os.makedirs(text_folder, exist_ok=True)
os.makedirs(ocr_folder, exist_ok=True)

MIN_TEXT_LENGTH = 80


def process_pdf(pdf_path, ocr_path):
    # Step 1 — OCR (only if not already done)
    if not os.path.exists(ocr_path):
        try:
            ocrmypdf.ocr(pdf_path, ocr_path, skip_text=True, deskew=True, quiet=True)
        except Exception as e:
            print("OCR failed:", e)
            return ""

    # Step 2 — Extract text
    text = ""

    try:
        with pdfplumber.open(ocr_path) as pdf:
            for page in pdf.pages:

                # tables
                for table in page.extract_tables() or []:
                    for row in table:
                        row = [c.strip() for c in row if c and c.strip()]
                        if row:
                            text += " | ".join(row) + "\n"

                # normal text
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        print("Extraction failed:", e)

    return text.strip()


print("\nProcessing PDFs...\n")

for file in os.listdir(pdf_folder):

    if not file.endswith(".pdf"):
        continue

    pdf_path = os.path.join(pdf_folder, file)
    ocr_path = os.path.join(ocr_folder, file)
    txt_path = os.path.join(text_folder, file.replace(".pdf", ".txt"))

    # skip if already processed
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            if len(f.read().strip()) >= MIN_TEXT_LENGTH:
                print("Skipping:", file)
                continue

    print("Processing:", file)

    text = process_pdf(pdf_path, ocr_path)

    if text:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print("Saved:", file)
    else:
        print("Failed:", file)

print("\nDone\n")