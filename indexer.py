import os
import json
from preprocess import preprocess
from database import get_connection, create_tables

text_folder = "data/text"
pdf_folder  = "data/pdfs"


def chunk_text(text, chunk_size=3):
    chunks = []
    paragraph_sentences = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if "|" in line:
            if paragraph_sentences:
                for i in range(0, len(paragraph_sentences), chunk_size):
                    chunk = ". ".join(paragraph_sentences[i:i + chunk_size]).strip()
                    if len(chunk) > 20:
                        chunks.append(chunk)
                paragraph_sentences = []

            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) == 2:
                chunk = f"{parts[0]} is {parts[1]}."
            elif len(parts) > 2:
                chunk = f"{parts[0]} includes {', '.join(parts[1:])}."
            else:
                chunk = line
            chunks.append(chunk)

        else:
            sentences = [s.strip() for s in line.split(".") if s.strip()]
            paragraph_sentences.extend(sentences)

    if paragraph_sentences:
        for i in range(0, len(paragraph_sentences), chunk_size):
            chunk = ". ".join(paragraph_sentences[i:i + chunk_size]).strip()
            if len(chunk) > 20:
                chunks.append(chunk)

    return chunks


def load_meta(txt_filename):
    """Load metadata from the .meta.json file for this pdf, if it exists."""
    pdf_name  = txt_filename.replace(".txt", ".pdf")
    meta_path = os.path.join(pdf_folder, pdf_name + ".meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"url": "", "date": "", "title": ""}


def build_index():
    create_tables()
    conn = get_connection()
    cur  = conn.cursor()

    print("\nStarting Indexing\n")

    for file in os.listdir(text_folder):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(text_folder, file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        meta  = load_meta(file)
        url   = meta.get("url",   "")
        date  = meta.get("date",  "")
        title = meta.get("title", "")

        chunks = chunk_text(text)

        for chunk in chunks:
            # skip duplicate chunks
            cur.execute("SELECT id FROM documents WHERE content = ?", (chunk,))
            if cur.fetchone():
                continue

            print("Indexing:", chunk[:80])

            cur.execute(
                "INSERT INTO documents(name, content, path, date, title) VALUES(?, ?, ?, ?, ?)",
                (file, chunk, url, date, title)
            )

            doc_id = cur.lastrowid
            for word in set(preprocess(chunk)):
                cur.execute(
                    "INSERT INTO keywords(word, doc_id) VALUES(?, ?)",
                    (word, doc_id)
                )
    conn.commit()
    conn.close()
    print("\nIndexing Completed\n")

if __name__ == "__main__":
    build_index()