import os
from preprocess import preprocess
from database import get_connection, create_tables

text_folder = "data/text"

def build_index():
    create_tables()
    conn = get_connection()
    cur = conn.cursor()

    print("\nStarting Indexing\n")

    for file in os.listdir(text_folder):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(text_folder, file)
        print("Indexing:", file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        cur.execute(
            "SELECT id, content FROM documents WHERE name=?",
            (file,)
        )
        existing = cur.fetchone()

        if existing:
            doc_id, old_content = existing

            if old_content == text:
                print("Skipping unchanged file:", file)
                continue
            print("Updating existing file:", file)
            cur.execute(
                "UPDATE documents SET content=?, path=? WHERE id=?",
                (text, path, doc_id)
            )
            cur.execute(
                "DELETE FROM keywords WHERE doc_id=?",
                (doc_id,)
            )
        else:
            cur.execute(
                "INSERT INTO documents(name, content, path) VALUES(?, ?, ?)",
                (file, text, path)
            )
            doc_id = cur.lastrowid
        words = preprocess(text)
        for word in words:
            cur.execute(
                "INSERT INTO keywords(word, doc_id) VALUES(?, ?)",
                (word, doc_id)
            )

    conn.commit()
    conn.close()

    print("\nIndexing Completed\n")
if __name__ == "__main__":
    build_index()