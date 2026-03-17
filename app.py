from flask import Flask, render_template, request, jsonify
from preprocess import expand_words, preprocess
from database import get_connection
import subprocess

app = Flask(__name__)


def get_best_sentence(content, query_words):
    sentences = content.split(".")
    best = ""
    best_score = 0

    for s in sentences:
        s_lower = s.lower()
        score = sum(1 for w in query_words if w in s_lower)

        if score > best_score:
            best_score = score
            best = s

    return best.strip() if best else content


def search_query(query):
    words = preprocess(query)
    words = expand_words(words)

    conn = get_connection()
    cur = conn.cursor()
    results = {}

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
            content = row[2]

            if doc_id not in results:
                results[doc_id] = {
                    "name": row[1],
                    "content": content,
                    "path": row[3],
                    "score": 0
                }

            # base score
            results[doc_id]["score"] += 1

            # phrase boost
            if query.lower() in content.lower():
                results[doc_id]["score"] += 5

    conn.close()

    if not results:
        return "Sorry, I couldn't find relevant information.", "", ""

    best = max(results.values(), key=lambda x: x["score"])

    best_answer = get_best_sentence(best["content"], words)
    return best_answer, best["name"], best["path"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.json["message"]
    answer, source, source_path = search_query(user_query)

    return jsonify({
        "answer": answer,
        "source": source,
        "path": source_path
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