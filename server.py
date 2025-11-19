import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ===== پیکربندی Gemini API =====
# GEMINI_API_KEY را در Render → Config vars قرار دهید
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("لطفاً GEMINI_API_KEY را در environment variables تنظیم کنید")

genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"  # یا هر مدل دیگری که می‌خواهید

# ===== مسیر دریافت متن =====
@app.route("/speech", methods=["POST"])
def speech_to_gemini():
    # متن دریافتی از ESP32
    text = request.get_data(as_text=True).strip()
    if not text:
        return jsonify({"error": "متن ارسال نشده"}), 400

    try:
        # ارسال متن به Gemini
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(text)
        answer = response.text

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== اجرای Flask =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
