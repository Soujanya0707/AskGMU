from flask import Flask, render_template, request, jsonify
from preprocess import expand_words, preprocess
from database import get_connection
import subprocess

app = Flask(__name__)

def get_best_chunk(content, query_words, chunk_size=1):

    sentences = content.replace("\n", " ").split(".")

    best_score = 0
    best_chunk = ""

    for i in range(len(sentences)):

        chunk = ". ".join(sentences[i:i+chunk_size])
        chunk_lower = chunk.lower()

        score = sum(1 for word in query_words if word in chunk_lower)

        if score > best_score:
            best_score = score
            best_chunk = chunk

    if best_chunk:
        return best_chunk.strip()

    return content[:300]



def search_query(query):
    words = preprocess(query)
    words = expand_words(words)

    conn = get_connection()
    cur = conn.cursor()
    results = {}

    for word in words:

        cur.execute("""
        SELECT documents.id, documents.name, documents.content
        FROM keywords
        JOIN documents
        ON keywords.doc_id = documents.id
        WHERE keywords.word = ?
        """, (word,))

        rows = cur.fetchall()

        for row in rows:

            doc_id = row[0]

            if doc_id not in results:
                results[doc_id] = {
                    "name": row[1],
                    "content": row[2],
                    "score": 0
                }

            results[doc_id]["score"] += 1

    conn.close()

    if not results:
        return "Sorry, I couldn't find relevant information.", ""

    # rank results by score
    best_doc = max(results.values(), key=lambda x: x["score"])

    
    answer = get_best_chunk(best_doc["content"], words)
    source = best_doc["name"]

    return answer, source

#routes
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    user_query = request.json["message"]

    answer, source = search_query(user_query)

    return jsonify({
        "answer": answer,
        "source": source
    })

#refresh data button (lateast update])
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