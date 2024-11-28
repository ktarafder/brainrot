import spacy
import emoji

SLANG_WORDS = ["bruh", "yeet", "sus", "pog", "lmao", "tbh"]
MEME_PHRASES = ["no cap", "on god", "big yikes", "say less"]

def slang_density(doc):
    slang_count = sum(1 for token in doc if token.text.lower() in SLANG_WORDS)
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
    
    # Calculate metrics
    slang_score = slang_density(doc)
    emoji_score = count_emojis(text) / len(doc) if len(doc) > 0 else 0
    meme_score = meme_density(text) / len(list(doc.sents)) if len(list(doc.sents)) > 0 else 0
    chaos_score = sentence_chaos(doc)
    
    # Weighted formula
    score = (slang_score * 0.4) + (emoji_score * 0.2) + (meme_score * 0.2) + (chaos_score * 0.2)
    return min(score * 100, 100)  # Cap at 100

if __name__ == "__main__":
    # Test Texts
    text1 = "Bruh, no cap, this is sus!!! 😂😂😂 Say less."
    text2 = "This is a formal sentence. It is structured and coherent no cap."

    # Calculate scores
    score1 = brainrot_score(text1)
    score2 = brainrot_score(text2)

    print(f"Text 1 Brainrot Score: {score1}")
    print(f"Text 2 Brainrot Score: {score2}")



