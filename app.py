from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/career')
def career():
    return render_template('career.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/interview')
def interview():
    return render_template('interview.html')

from flask import request, jsonify
import os
from services.career_service import generate_career_plan
from services.resume_service import process_resume
from services.interview_service import generate_mcq_test, save_interview_result, get_interview_history
from dotenv import load_dotenv

load_dotenv()

# Create uploads dir
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/career-plan', methods=['POST'])
def career_plan():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided. Please fill out the form."}), 400
        
    plan, error = generate_career_plan(data)
    
    if error:
        return jsonify({"error": error}), 500
        
    return jsonify(plan)

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    if 'resumeFile' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['resumeFile']
    target_role = request.form.get('jobDescription', '')
    
    result, error = process_resume(file, target_role, app.config['UPLOAD_FOLDER'])
    
    if error:
        return jsonify({"error": error}), 500
        
    return jsonify(result)

@app.route('/api/generate-interview', methods=['POST'])
def generate_interview():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided."}), 400
        
    quiz, error = generate_mcq_test(data)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(quiz)

@app.route('/api/save-interview-result', methods=['POST'])
def save_interview():
    data = request.json
    save_interview_result(data)
    return jsonify({"success": True})

@app.route('/api/interview-history', methods=['GET'])
def interview_history():
    history = get_interview_history()
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
