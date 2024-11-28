from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
import spacy
import emoji

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Brainrot-related constants
BRAINROT = [
    "skibidi", "gyatt", "rizz", "duke dennis", 
    "sussy imposter", "sigma", "alpha", "beta", "omega", "grindset", "gooning",
    "copium", "cope", "seethe", "mald", "cringe", "based", "redpilled", "bluepilled", "blackpilled",
    "omega male grindset", "andrew tate", "goon cave", 
    "blud", "dawg", "ishowspeed", "kai cenat", "fanum tax", "bussing", "adin ross", 
    "grimace shake", "amogus", "poggers", "glizzy", "thug shaker", 
    "morbin time", "dj khaled", "sisyphus", "oceangate",
    "nickeh30", "ratio", "uwu", "delulu", "mewing", "gta 6", 
    "backrooms", "gigachad", "based", "kino", "no cap", "mrbeast", "ice spice",
    "subway surfers"
]

MEME_PHRASES = [
    "cap", "on god", "big yikes", "say less", "goofy ahh", "only in ohio", 
    "the ocky way", "whopper whopper whopper whopper", "1 2 buckle my shoe", 
    "sin city", "monday left me broken", "ayo the pizza here", 
    "family guy funny moments compilation with subway surfers gameplay at the bottom", 
    "F in the chat", "i love lean", "looksmaxxing", "better call saul", 
    "i guess they never miss huh", "kid named finger", "no nut november", "bing chilling",
    "sussy baka", "among us", "rizzing up baby gronk", "i like ya cut g", "i am a surgeon",
    "chill guy", "brazil", "Ws in the chat", "metal pipe falling", "did you pray today",
    "livvy dunne", "ugandan knuckles", "social credit", "foot fetish", "better caul saul",
    "freddy fazbear", "literally hitting the griddy", "bro really thinks he's carti",
    "a whole bunch of turbulence", "don pollo", "quandale dingle", "lightskin stare",
    "john pork", "all my fellas", "colleen ballinger", "smurf cat vs strawberry elephant",
    "fr we go gym", "goated with the sauce", "kevin james", "chill guy", "kiki do you love me", "hit or miss",
    "zesty ahh", "rose toy", "having a great day"
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def parse_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text

def parse_word(file_path):
    document = Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n\n"
    return text

def slang_density(doc):
    slang_count = sum(1 for token in doc if token.text.lower() in BRAINROT)
    return slang_count / len(doc) if len(doc) > 0 else 0

def meme_density(text):
    return sum(1 for phrase in MEME_PHRASES if phrase in text.lower())

def count_emojis(text):
    return sum(1 for char in text if char in emoji.EMOJI_DATA)

def sentence_chaos(doc):
    sentence_lengths = [len(sentence.text.split()) for sentence in doc.sents]
    return max(sentence_lengths) - min(sentence_lengths) if len(sentence_lengths) > 1 else 0

def brainrot_score(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    slang_score = slang_density(doc)
    emoji_score = count_emojis(text) / len(doc) if len(doc) > 0 else 0
    meme_score = meme_density(text) / len(list(doc.sents)) if len(list(doc.sents)) > 0 else 0
    chaos_score = sentence_chaos(doc)
    
    score = (slang_score * 0.4) + (emoji_score * 0.2) + (meme_score * 0.2) + (chaos_score * 0.2)
    return min(score * 100, 100)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format. Only PDF and DOCX are supported.'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Parse the file based on its type
    file_type = filename.rsplit('.', 1)[1].lower()
    if file_type == 'pdf':
        text = parse_pdf(file_path)
    elif file_type == 'docx':
        text = parse_word(file_path)
    else:
        return jsonify({'error': 'Unsupported file type.'}), 400

    # Calculate bot scorerainr
    score = brainrot_score(text)
    return jsonify({'brainrot_score': score})

if __name__ == '__main__':
    app.run(debug=True)
