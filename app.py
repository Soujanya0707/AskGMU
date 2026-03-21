from flask import Flask, render_template, request, jsonify
from preprocess import expand_words, preprocess
from database import get_connection
import subprocess
import os

app = Flask(__name__)

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

    result = ". ".join(s for score, s in top_sorted)
    return result + "." if result else content

def search_query(query):
    words = preprocess(query)
    words = expand_words(words)

    conn = get_connection()
    cur = conn.cursor()

    # score at chunk level
    doc_scores = {}

    for word in words:
        cur.execute("""
            SELECT documents.id, documents.name, documents.content, documents.path
            FROM keywords
            JOIN documents
            ON keywords.doc_id = documents.id
            WHERE keywords.word = ?
            LIMIT 50
        """, (word,))

        rows = cur.fetchall()

        for row in rows:
            doc_id = row[0]
            name = row[1]
            content = row[2]
            path = row[3]

            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    "name": name,
                    "content": content,
                    "path": path,
                    "score": 0
                }

            # base score
            doc_scores[doc_id]["score"] += 1

            # phrase boost
            if query.lower() in content.lower():
                doc_scores[doc_id]["score"] += 5

    conn.close()

    if not doc_scores:
        return "Sorry, I couldn't find relevant information.", []

    ranked = sorted(doc_scores.values(), key=lambda x: x["score"], reverse=True)

    file_scores = {}
    for doc in ranked:
        name = doc["name"]
        if name not in file_scores:
            file_scores[name] = {"chunks": [], "score": 0}
        file_scores[name]["chunks"].append(doc["content"])
        file_scores[name]["score"] += doc["score"]

    best_file = max(file_scores.values(), key=lambda x: x["score"])

    # combine only chunks from that single best file
    combined_content = " ".join(best_file["chunks"][:5])
    best_answer = get_best_sentence(combined_content, words)

    seen_names = []
    top_sources = []

    for doc in ranked:
        pdf_name = doc["name"].replace(".txt", ".pdf")
        if pdf_name not in seen_names:
            seen_names.append(pdf_name)

            url_file = os.path.join("data/pdfs", pdf_name + ".url")
            if os.path.exists(url_file):
                with open(url_file, "r") as f:
                    path = f.read().strip()
            else:
                path = os.path.join("data/pdfs", pdf_name)

            top_sources.append({
                "name": pdf_name,
                "path": path
            })
        if len(top_sources) == 5:
            break

    return best_answer, top_sources

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.json["message"]
    answer, sources = search_query(user_query)

    return jsonify({
        "answer": answer,
        "sources": sources  # list of {name, path}
    })


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