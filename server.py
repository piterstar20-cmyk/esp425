import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ---- LOCAL API KEY (set in Render environment variables) ----
# In Render dashboard: Config vars → add GEMINI_API_KEY = <your-key>
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"      # or gemini-1.5-pro, etc.

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' in JSON"}), 400

    prompt = data["prompt"]
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        answer = response.text
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render supplies PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

