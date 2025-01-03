from flask import Flask, request, jsonify
import sqlite3
import openai
import os

app = Flask(__name__)

# Configure OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database Connection Function
def get_db_connection():
    conn = sqlite3.connect('resources.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return "Welcome to the AI Resource Finder!"

@app.route('/get-resources', methods=['POST'])
def get_resources():
    data = request.json
    exam = data.get('exam', '').strip()
    language = data.get('language', '').strip()
    experience_level = data.get('experience_level', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT resource FROM resources 
                      WHERE exam = ? AND language = ? AND experience_level = ?''',
                   (exam, language, experience_level))
    results = cursor.fetchall()
    conn.close()

    if results:
        return jsonify({"resources": [row['resource'] for row in results]})

    # Fallback to OpenAI API
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Suggest some learning resources for {exam} exam preparation in {language} for a {experience_level} level student.",
            max_tokens=100
        )
        ai_resources = response.choices[0].text.strip().split('\n')
        return jsonify({"resources": ai_resources})
    except Exception as e:
        return jsonify({"error": "Unable to fetch resources.", "details": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
