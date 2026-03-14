from flask import Flask, render_template, request, jsonify
import time
import os
import sys
 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
app = Flask(__name__)
 
@app.route("/")
def index():
    return render_template("index.html")
 
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "").strip()
    url = data.get("url", "").strip()
 
    if not text and not url:
        return jsonify({"error": "Please paste some brand content first."}), 400
 
    time.sleep(1)  # small delay so loading animation is visible
 
    try:
        from mock_modules import get_mock_analysis, run_pipeline
 
        use_mocks = os.getenv("USE_MOCKS", "true").lower() == "true"
 
        if use_mocks:
            result = get_mock_analysis(text or url)
        else:
            # Day 4: teammates' real modules kick in here
            result = run_pipeline(text or url)
 
        return jsonify(result)
 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
if __name__ == "__main__":
    app.run(debug=True, port=5000)