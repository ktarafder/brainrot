from flask import Flask, request, render_template
import os
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
import spacy
import emoji
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Brainrot-related constants
BRAINROT = [
    "skibidi", "gyatt", "rizz", "duke dennis", 
    "sussy imposter",  "sigma", "alpha", "beta", "omega", "grindset", "gooning",
    "copium", "cope", "seethe", "mald", "cringe", "based", "redpilled", "bluepilled", "blackpilled",
    "omega male grindset", "andrew tate", "goon cave", 
    "blud", "dawg", "ishowspeed", "kai cenat", "fanum tax", "bussing", "adin ross", 
    "grimace shake", "amogus", "poggers", "glizzy", "thug shaker", 
    "morbin time", "dj khaled", "sisyphus", "oceangate"
    "nickeh30", "ratio", "uwu", "delulu", "mewing", "gta 6", 
    "backrooms", "gigachad", "based", "kino", "no cap", "mrbeast", "ice spice",
    "subway surfers", "crashing out", "huzz", "chuzz", "kitten", "gng", "top"
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
    "zesty ahh", "rose toy", "having a great day", "w message"
]

EMOJI_WEIGHTS = {
    "🍆": 2.0,
    "👅": 2.0,
    "🍑": 2.0,
    "🥵": 1.7,
    "😈": 1.5,
    "🤬": 1.4,
    "😍": 1.4,
    "👺": 1.4,
    "🤷‍♀️": 1.0,
    "❌": 1.2,
    "🚫": 1.2,
    "🥵": 1.5,
    "🧏‍♂": 1.9,
    "💅": 1.9,
    "🚽": 1.7,
    "🤡": 1.7,
    "‼️": 1.5,
    "🤖": 1.3,
    "🤯": 1.7,
    "🤠": 1.5,
    "🤑": 1.2,
    "🤫": 1.5,
    "🤥": 1.3,
    "🤧": 1.3,
    "🥺": 1.5,
    "😎": 1.2,
    "😜": 1.4,
    "🤪": 1.7,
    "👼": 1.1,
    "💀": 1.5,
    "👑": 1.1,
}

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

def adjusted_slang_density(doc):
    slang_count = sum(1 for token in doc if token.text.lower() in BRAINROT)
    return slang_count / np.sqrt(len(doc)) if len(doc) > 0 else 0  # Square root scaling

def adjusted_meme_density(text, num_sentences):
    meme_count = sum(1 for phrase in MEME_PHRASES if phrase in text.lower())
    return meme_count / np.sqrt(num_sentences) if num_sentences > 0 else 0  # Square root scaling

def normalized_emoji_score(text, num_tokens):
    emoji_score = sum(EMOJI_WEIGHTS.get(char, 1) for char in text if char in emoji.EMOJI_DATA)
    return emoji_score / np.sqrt(num_tokens) if num_tokens > 0 else 0

def scaled_sentence_chaos(doc):
    sentence_lengths = [len(sentence.text.split()) for sentence in doc.sents]
    chaos = max(sentence_lengths) - min(sentence_lengths) if len(sentence_lengths) > 1 else 0
    return chaos / len(doc) if len(doc) > 0 else 0  # Normalize by total token count

def refined_brainrot_score(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    num_tokens = len(doc)
    print(num_tokens)
    num_sentences = len(list(doc.sents))
    print(num_sentences)

    # Calculate metrics
    slang_score = adjusted_slang_density(doc)
    emoji_score = normalized_emoji_score(text, num_tokens)
    meme_score = adjusted_meme_density(text, num_sentences)
    chaos_score = scaled_sentence_chaos(doc)

    # Weighted formula
    score = (
        (slang_score * 0.5) +  # Slang has the most weight
        (emoji_score * 0.2) +  # Emojis contribute moderately
        (meme_score * 0.2) +   # Meme phrases have a similar impact to emojis
        (chaos_score * 0.1)    # Chaos contributes less for balance
    )
    return min(score * 100, 100)  # Cap at 100

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
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
                return "Unsupported file type."

            # Calculate brainrot score
            score = refined_brainrot_score(text)

            return f"""
            <!doctype html>
            <title>Brainrot Score</title>
            <h1>Brainrot Score: {score:.2f}</h1>
            <a href="/">Upload another file</a>
            """
        else:
            return "Invalid file format. Only PDF and DOCX are supported."

    return '''
    <!doctype html>
    <title>Brainrot Analyzer</title>
    <h1>Upload PDF or DOCX File</h1>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)