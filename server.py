import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import json
import re

app = Flask(__name__)

# API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"

FORMAT_PROMPT = """
First translate the text into English and then
You are an IoT command parser. 

Extract:
- device: red, green, or blue
- action: on or off
- delay: integer

Return ONLY pure JSON.
No markdown.
No code fences.
No explanation.

Example input:
"green light on for 3 seconds"

Output:
{"device":"green","action":"on","delay":3}
"""


def clean_json(text):
    """Remove ```json  ``` and extract the actual JSON."""
    
    # Remove code fences
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()

    # Try to extract JSON part using regex
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        return match.group(0)

    return text  # fallback


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt'"}), 400

    user_prompt = data["prompt"]
    final_prompt = FORMAT_PROMPT + "\nUser Input: " + user_prompt

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(final_prompt)
        raw = response.text.strip()

        cleaned = clean_json(raw)

        # Attempt to parse cleaned text
        try:
            parsed = json.loads(cleaned)
            return jsonify(parsed)

        except json.JSONDecodeError:
            return jsonify({
                "error": "Invalid JSON after cleaning",
                "raw": raw,
                "cleaned": cleaned
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
