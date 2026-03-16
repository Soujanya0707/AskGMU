import os
import PyPDF2
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# folders
pdf_folder = "data/pdfs"
text_folder = "data/text"

os.makedirs(text_folder, exist_ok=True)

MIN_TEXT_LENGTH = 80

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
        return ""

    return text

def extract_pdf_text_ocr(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path, poppler_path=r"C:\poppler-25.12.0\Library\bin")
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
    except Exception as e:
        print("OCR failed:", pdf_path, "→", e)
        return ""
    return text

print("\nStarting PDF Processing\n")

for file in os.listdir(pdf_folder):

    if file.endswith(".pdf"):

        txt_name = file.replace(".pdf", ".txt")
        txt_path = os.path.join(text_folder, txt_name)

        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                existing_text = f.read().strip()
            if len(existing_text) >= MIN_TEXT_LENGTH:
                print("Skipping existing:", file)
                continue
            print("Reprocessing weak text file:", file)

        pdf_path = os.path.join(pdf_folder, file)
        print("Processing:", file)
        text = extract_pdf_text(pdf_path)

        if len(text.strip()) < MIN_TEXT_LENGTH:  # changed from "not text.strip()"
            print("Trying OCR for:", file)
            text = extract_pdf_text_ocr(pdf_path)

        if not text.strip():
            print("Skipping empty file:", file)
        else:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
print("\nPDF Processing Completed\n")