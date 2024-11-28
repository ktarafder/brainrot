from flask import Flask, request, render_template
import os
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
import spacy
import emoji
import numpy as np
from spacy.matcher import PhraseMatcher

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Single-word slang
BRAINROT = [
    "skibidi", "gyatt", "rizz", "sigma", "alpha", "beta", "omega", "grindset",
    "amogus", "sus", "imposter", "sussy", "impostor", "suspect", "amongus",
    "gooning", "goon", "gooner", "kpop", 
    "boomer", "doomer", "zoomer",
    "copium", "cope", "seethe", "mald", "cringe", "based", "redpilled",
    "bluepilled", "blackpilled", "blud", "dawg", "ishowspeed", "bussing", "poggers",
    "glizzy", "thug", "slatt", "twin"
]

# Multi-word slang phrases
BRAINROT_PHRASES = [
    "top g", "omega male grindset", "shadow wizard money gang", "high key", "low key", "no cap",
    "fanum tax", "kai cenat", "duke dennis", "adin ross", "andrew tate", "nickeh30", "ice spice", 
    "grimace shake", "morbin time", "dj khaled", "sisyphus", "oceangate",
]

# Multi-word meme phrases
MEME_PHRASES = [
    "cap", "on god", "big yikes", "say less", "goofy ahh", "only in ohio",
    "the ocky way", "whopper whopper whopper whopper", "1 2 buckle my shoe",
    "sin city", "monday left me broken", "ayo the pizza here",
    "family guy funny moments compilation with subway surfers gameplay at the bottom",
    "F in the chat", "i love lean", "looksmaxxing", "better call saul",
    "i guess they never miss huh", "kid named finger", "bing chilling", "sussy baka",
    "among us", "rizzing up baby gronk", "i like ya cut g", "i am a surgeon",
    "chill guy", "brazil", "Ws in the chat", "metal pipe falling", "did you pray today",
    "ugandan knuckles", "social credit", "better caul saul", "freddy fazbear",
    "literally hitting the griddy", "john pork", "all my fellas", "fr we go gym",
    "goated with the sauce", "kiki do you love me", "hit or miss", "zesty ahh", "touch grass",
    "monkeypox"
]

EMOJI_WEIGHTS = {
    "🍆": 2.0, "👅": 2.0, "🍑": 2.0, "🥵": 1.7, "😈": 1.5, "🤬": 1.4,
    "😍": 1.4, "🤷‍♀️": 1.0, "❌": 1.2, "🚫": 1.2, "💀": 1.5, "👑": 1.1,
    "🤖": 1.3, "🤯": 1.7, "🤪": 1.7, "👼": 1.1, "💅": 1.9, "😜": 1.4, "😎": 1.2
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

def create_phrase_matcher(nlp, phrases):
    """Create a PhraseMatcher for multi-word phrases."""
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(phrase) for phrase in phrases]
    matcher.add("PHRASE_MATCHER", patterns)
    return matcher

def adjusted_slang_density(doc, matcher):
    """Calculate slang density, including single words and multi-word phrases."""
    # Token-level slang matches
    slang_count = sum(1 for token in doc if token.text.lower() in BRAINROT)
    
    # Phrase-level slang matches
    matches = matcher(doc)
    
    # Total matches
    total_matches = slang_count + len(matches)
    return total_matches / np.sqrt(len(doc)) if len(doc) > 0 else 0

def adjusted_meme_density(doc, matcher, num_sentences):
    """Calculate meme density using PhraseMatcher."""
    matches = matcher(doc)  # Find matches in the document
    return len(matches) / np.sqrt(num_sentences) if num_sentences > 0 else 0

def normalized_emoji_score(text, num_tokens):
    """Calculate emoji score with weighted scaling."""
    emoji_score = sum(EMOJI_WEIGHTS.get(char, 1) for char in text if char in emoji.EMOJI_DATA)
    return emoji_score / np.sqrt(num_tokens) if num_tokens > 0 else 0

def scaled_sentence_chaos(doc):
    """Measure variability in sentence length."""
    sentence_lengths = [len(sentence.text.split()) for sentence in doc.sents]
    chaos = max(sentence_lengths) - min(sentence_lengths) if len(sentence_lengths) > 1 else 0
    return chaos / len(doc) if len(doc) > 0 else 0  # Normalize by total token count

def refined_brainrot_score(text):
    """Calculate the refined brainrot score."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    num_tokens = len(doc)
    num_sentences = len(list(doc.sents))
    
    # Create PhraseMatchers
    slang_matcher = create_phrase_matcher(nlp, BRAINROT_PHRASES)
    meme_matcher = create_phrase_matcher(nlp, MEME_PHRASES)
    
    # Calculate metrics
    slang_score = adjusted_slang_density(doc, slang_matcher)
    emoji_score = normalized_emoji_score(text, num_tokens)
    meme_score = adjusted_meme_density(doc, meme_matcher, num_sentences)
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