import os
import PyPDF2

# folders
pdf_folder = "data/pdfs"
text_folder = "data/text"

os.makedirs(text_folder, exist_ok=True)


def extract_pdf_text(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("Error reading:", pdf_path, "→", e)
        return ""   # explicit — makes intent clear

    if not text.strip():
        print("Warning: No text extracted from", pdf_path)
        print("PDF may be scanned/image-based — try OCR instead")

    return text


print("\nStarting PDF Processing\n")

for file in os.listdir(pdf_folder):

    if file.endswith(".pdf"):

        txt_name = file.replace(".pdf", ".txt")
        txt_path = os.path.join(text_folder, txt_name)

        if os.path.exists(txt_path):          # add this
            print("Skipping existing:", file)
            continue

        pdf_path = os.path.join(pdf_folder, file)

        print("Processing:", file)

        text = extract_pdf_text(pdf_path)

        if not text.strip():
            print("Skipping empty file:", file)
        else:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
print("\nPDF Processing Completed\n")