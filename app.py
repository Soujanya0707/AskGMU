from flask import Flask, render_template, request, jsonify
from preprocess import expand_words, preprocess
from database import get_connection
import subprocess
import os
from datetime import datetime

app = Flask(__name__)

RECENCY_KEYWORDS = {
    "latest", "new", "newest", "recent", "today",
    "current", "fresh", "last", "update", "updated"
}

def parse_date(date_str):
    """Parse DD/MM/YYYY → datetime. Returns datetime.min on failure."""
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y")
    except Exception:
        return datetime.min

def is_recency_query(query):
    words = set(query.lower().split())
    return bool(words & RECENCY_KEYWORDS)

def get_best_sentence(content, query_words, max_sentences=5):
    sentences = [s.strip() for s in content.split(".") if len(s.strip()) > 15]

    seen = []
    unique_sentences = []
    for s in sentences:
        if s not in seen:
            seen.append(s)
            unique_sentences.append(s)
    sentences = unique_sentences

    scored_sentences = []
    for s in sentences:
        s_lower = s.lower()
        score = sum(1 for w in query_words if w in s_lower)
        scored_sentences.append((score, s))

    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    top = scored_sentences[:max_sentences]
    top_sorted = sorted(top, key=lambda x: sentences.index(x[1]))

    result = ". ".join(s for _, s in top_sorted)
    return result + "." if result else content

def search_query(query):
    words    = preprocess(query)
    words    = expand_words(words)
    recency  = is_recency_query(query)

    conn = get_connection()
    cur  = conn.cursor()
    doc_scores = {}

    for word in words:
        cur.execute("""
            SELECT documents.id, documents.name, documents.content,
                   documents.path, documents.date, documents.title
            FROM keywords
            JOIN documents ON keywords.doc_id = documents.id
            WHERE keywords.word = ?
            LIMIT 50
        """, (word,))

        for row in cur.fetchall():
            doc_id, name, content, path, date, title = row

            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    "name":    name,
                    "content": content,
                    "path":    path,
                    "date":    date  or "",
                    "title":   title or "",
                    "score":   0
                }

            doc_scores[doc_id]["score"] += 1

            if query.lower() in content.lower():
                doc_scores[doc_id]["score"] += 5

    conn.close()

    if not doc_scores:
        return "Sorry, I couldn't find relevant information.", []

    ranked = sorted(doc_scores.values(), key=lambda x: x["score"], reverse=True)

    # ── deduplicate by pdf name, collect top sources ────────────────────────
    seen_names  = []
    top_sources = []

    for doc in ranked:
        pdf_name = doc["name"].replace(".txt", ".pdf")
        if pdf_name in seen_names:
            continue
        seen_names.append(pdf_name)

        top_sources.append({
            "name":  doc["title"] if doc["title"] else pdf_name,
            "file":  pdf_name,
            "path":  doc["path"] if doc["path"] else os.path.join("data/pdfs", pdf_name),
            "date":  doc["date"],
        })

        if len(top_sources) == 10:
            break

    # ── recency query → sort by date, answer from freshest doc ─────────────
    if recency:
        top_sources.sort(key=lambda s: parse_date(s["date"]), reverse=True)

        best_name = top_sources[0]["file"].replace(".pdf", ".txt")
        conn2 = get_connection()
        cur2  = conn2.cursor()
        cur2.execute(
            "SELECT content FROM documents WHERE name = ? LIMIT 1", (best_name,)
        )
        row = cur2.fetchone()
        conn2.close()

        best_content = row[0] if row else ""
        if best_content:
            answer = get_best_sentence(best_content, words)
        else:
            answer = (f"The latest notice is dated {top_sources[0]['date']}: "
                      f"{top_sources[0]['name']}")
    else:
        # ── normal relevance ranking 
        file_scores = {}
        for doc in ranked:
            n = doc["name"]
            if n not in file_scores:
                file_scores[n] = {"chunks": [], "score": 0}
            file_scores[n]["chunks"].append(doc["content"])
            file_scores[n]["score"] += doc["score"]

        best_file = max(file_scores.values(), key=lambda x: x["score"])
        combined  = " ".join(best_file["chunks"][:5])
        answer    = get_best_sentence(combined, words)

    return answer, top_sources[:5]


# ── routes 

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.json["message"]
    answer, sources = search_query(user_query)
    return jsonify({"answer": answer, "sources": sources})

@app.route("/refresh")
def refresh():
    try:
        subprocess.run(["python", "scraper.py"])
        subprocess.run(["python", "pdf_processor.py"])
        subprocess.run(["python", "indexer.py"])
        return jsonify({"message": "Data refreshed successfully"})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)