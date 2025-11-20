import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ---- LOCAL API KEY (set in Render environment variables) ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' in JSON"}), 400

    prompt = data["prompt"]

    try:
        # ساخت پرامتی که فقط تحلیل احساس را برمی‌گرداند
        full_prompt = f"""
        متن زیر را تحلیل احساسات کن.
        فقط یکی از این سه کلمه را بنویس:
        مثبت
        منفی
        خنثی

        متن:
        {prompt}
        """

        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(full_prompt)

        sentiment = response.text.strip()

        # اطمینان از برگرداندن یکی از سه مقدار
        valid = ["مثبت", "منفی", "خنثی"]
        if sentiment not in valid:
            sentiment = "خنثی"

        return jsonify({"answer": sentiment})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
