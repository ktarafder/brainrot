import spacy
import emoji
import numpy as np

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
    "subway surfers", "crashing out", "huzz", "chuzz", "kitten"
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

def slang_density(doc):
    slang_count = sum(1 for token in doc if token.text.lower() in BRAINROT)
    return slang_count / len(doc) if len(doc) > 0 else 0

def meme_density(text):
    return sum(1 for phrase in MEME_PHRASES if phrase in text.lower())

def enhanced_emoji_score(text):
    return sum(EMOJI_WEIGHTS.get(char, 1) for char in text if char in emoji.EMOJI_DATA)

def sentence_chaos(doc):
    sentence_lengths = [len(sentence.text.split()) for sentence in doc.sents]
    return max(sentence_lengths) - min(sentence_lengths) if len(sentence_lengths) > 1 else 0

def brainrot_score(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    # Calculate metrics
    slang_score = slang_density(doc)
    emoji_score = enhanced_emoji_score(text) / len(doc) if len(doc) > 0 else 0
    meme_score = meme_density(text) / len(list(doc.sents)) if len(list(doc.sents)) > 0 else 0
    chaos_score = sentence_chaos(doc)
    
    # Weighted formula
    score = (slang_score * 0.4) + (emoji_score * 0.2) + (meme_score * 0.2) + (chaos_score * 0.2)
    return min(score * 100, 100)  # Cap at 100

if __name__ == "__main__":
    # Test Texts
    text1 = "This is a normal sentence on god. I love to see it. I guess they never miss huh. 1 2 buckle my shoe. Skibidi bop bop bop🍆"
    text2 = "Skibidi bop bop bop, gyatt, the rizz levels in Ohio are off the  charts, and somewhere Duke Dennis is asking, “Did you pray today?” Meanwhile, Livvy Dunne is out here rizzing up Baby  Gronk with that sussy imposter energy—pibby glitching reality "

    # Calculate scores
    score1 = brainrot_score(text1)
    score2 = brainrot_score(text2)

    print(f"Text 1 Brainrot Score: {score1}")
    print(f"Text 2 Brainrot Score: {score2}")



