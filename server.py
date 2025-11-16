import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import json

app = Flask(__name__)

# ---- API KEY from Render env ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in Render environment variables")

genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"

# -----------------------------
# FORCE GEMINI TO RETURN JSON
# -----------------------------
JSON_PROMPT = """
You are a command parser for an IoT system.

Extract the following fields from the user's text:
- device : one of ["red", "green", "blue"]
- action : one of ["on", "off"]
- delay : integer number of seconds (default 0 if not provided)

Format output ONLY as raw JSON, no explanations.

Example:
Input: "green light on for 3 seconds"
Output:
{"device":"green", "action":"on", "delay":3}
"""


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' in JSON"}), 400

    user_prompt = data["prompt"]

    # Final prompt to Gemini
    final_prompt = JSON_PROMPT + "\nUser Input: " + user_prompt

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(final_prompt)
        raw_text = response.text.strip()

        # Try to parse JSON safely
        try:
            parsed = json.loads(raw_text)
            return jsonify(parsed)
        except json.JSONDecodeError:
            return jsonify({"error": "Gemini returned invalid JSON", "raw": raw_text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
