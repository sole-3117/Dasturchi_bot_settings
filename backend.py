from flask import Flask, request, jsonify
import json

app = Flask(__name__)

def load(filename):
    with open(filename, "r") as f:
        return json.load(f)

def save(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/get_snippet")
def get_snippet():
    user_id = request.args.get("user_id")
    snippets = load("snippets.json")
    progress = load("progress.json")

    user = progress.get(user_id, {
        "current_id": snippets[0]["id"],
        "written": "",
        "completed_ids": []
    })

    current = next((s for s in snippets if s["id"] == user["current_id"]), snippets[0])

    return jsonify({
        "id": current["id"],
        "text": current["text"],
        "written": user["written"]
    })

@app.route("/submit_code", methods=["POST"])
def submit_code():
    data = request.get_json()
    user_id = data["user_id"]
    snippet_id = data["snippet_id"]
    written = data["written"]

    snippets = load("snippets.json")
    progress = load("progress.json")

    snippet = next((s for s in snippets if s["id"] == snippet_id), None)
    if not snippet:
        return jsonify({"error": "Not found"}), 404

    correct = written.strip() == snippet["text"].strip()

    if user_id not in progress:
        progress[user_id] = {
            "current_id": snippet_id,
            "written": "",
            "completed_ids": []
        }

    if correct:
        progress[user_id]["completed_ids"].append(snippet_id)
        next_snippet = next((s for s in snippets if s["id"] not in progress[user_id]["completed_ids"]), None)
        progress[user_id]["current_id"] = next_snippet["id"] if next_snippet else None
        progress[user_id]["written"] = ""
    else:
        progress[user_id]["written"] = written

    save("progress.json", progress)
    return jsonify({"correct": correct})

if __name__ == "__main__":
    app.run(debug=True)