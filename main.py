from flask import Flask, request, jsonify
import sqlite3
import openai
import os

app = Flask(__name__)

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database Initialization
def init_db():
    conn = sqlite3.connect('resources.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS resources (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        exam TEXT,
                        language TEXT,
                        experience_level TEXT,
                        resource TEXT
                    )''')
    conn.commit()
    conn.close()

# Seed the database with sample data
def seed_db():
    conn = sqlite3.connect('resources.db')
    cursor = conn.cursor()
    sample_data = [
        ('CDS', 'English', 'Beginner', 'https://cds-beginner-english.com'),
        ('CDS', 'Telugu', 'Beginner', 'https://cds-beginner-telugu.com'),
        ('CDS', 'English', 'Intermediate', 'https://cds-intermediate-english.com')
    ]
    cursor.executemany('''INSERT INTO resources (exam, language, experience_level, resource) VALUES (?, ?, ?, ?)''', sample_data)
    conn.commit()
    conn.close()

# Flask Routes
@app.route('/')
def home():
    return "Welcome to the AI Resource Finder!"

@app.route('/get-resources', methods=['POST'])
def get_resources():
    user_input = request.json
    exam = user_input.get('exam', '').strip()
    language = user_input.get('language', '').strip()
    experience_level = user_input.get('experience_level', '').strip()

    # Search in the database
    conn = sqlite3.connect('resources.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT resource FROM resources WHERE exam = ? AND language = ? AND experience_level = ?''',
                   (exam, language, experience_level))
    results = cursor.fetchall()
    conn.close()

    if results:
        resources = [row[0] for row in results]
        return jsonify({"resources": resources})

    # If no results, use OpenAI to generate suggestions
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Suggest some learning resources for {exam} exam preparation in {language} for a {experience_level} level student.",
            max_tokens=100
        )
        ai_resources = response.choices[0].text.strip().split('\n')
        return jsonify({"resources": ai_resources})
    except Exception as e:
        return jsonify({"error": "Could not fetch AI-generated resources.", "details": str(e)})

if __name__ == "__main__":
    init_db()
    seed_db()
    app.run(debug=True)
