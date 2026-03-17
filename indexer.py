import os
from preprocess import preprocess
from database import get_connection, create_tables

text_folder = "data/text"


def chunk_text(text, chunk_size=2):
    chunks = []
    paragraph_sentences = []

    lines = text.split("\n")

    for line in lines:
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


def build_index():
    create_tables()
    conn = get_connection()
    cur = conn.cursor()

    print("\nStarting Indexing\n")

    for file in os.listdir(text_folder):
        if not file.endswith(".txt"):