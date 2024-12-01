from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from nlp import refined_brainrot_score, suggest_brainrotted_text

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if the file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def parse_pdf(file_path):
    """Extract text from a PDF file."""
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text

def parse_word(file_path):
    """Extract text from a Word document."""
    document = Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n\n"
    return text

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint to handle file uploads, calculate brainrot score, and generate suggestions."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part provided"}), 400
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_extension = filename.rsplit('.', 1)[1].lower()
        if file_extension == 'pdf':
            text = parse_pdf(file_path)
        elif file_extension == 'docx':
            text = parse_word(file_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        brainrot_score = refined_brainrot_score(text)
        suggestions = suggest_brainrotted_text(text, brainrot_score)
        if isinstance(suggestions, list):
            suggestions = [str(s) for s in suggestions]
        else:
            suggestions = [str(suggestions)]

        return jsonify({
            "score": round(brainrot_score, 2),
            "suggestions": suggestions
        }), 200
    
    return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(debug=True)