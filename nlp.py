import spacy
from spacy.matcher import PhraseMatcher
import emoji
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os

# Single-word slang
BRAINROT = [
    "skibidi", "gyatt", "rizz", "sigma", "alpha", "beta", "omega", "grindset",
    "amogus", "sus", "imposter", "sussy", "impostor", "suspect", "amongus",
    "gooning", "goon", "gooner", "kpop", 
    "boomer", "doomer", "zoomer", "gloomer",
    "copium", "cope", "seethe", "mald", "cringe", "based", "redpilled",
    "bluepilled", "blackpilled", "blud", "dawg", "ishowspeed", "bussing", "poggers",
    "glizzy", "thug", "slatt", "twin", "highkey", "lowkey", "bbc", "rawdogging"
]

# Multi-word slang phrases
BRAINROT_PHRASES = [
    "top g", "omega male grindset", "high key", "low key", "no cap",
    "fanum tax", "kai cenat", "duke dennis", "adin ross", "andrew tate", "nickeh30", "ice spice", "baby gronk", "dj khaled",
    "grimace shake", "morbin time", "sussy baka", "anumaanam yadava",
    "hawk tuah", "talk tuah", "crash out", "crashing out", "subway surfers", "when the impostor is sus",
    "type shit", "type shi", "raw dogging"
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
    "monkeypox", "big chungus", "oceangate", "lebron james", "he got that dawg in him",
    "spit on that thang", "i am speed"
]

EMOJI_WEIGHTS = {
    "🍆": 2.0, "👅": 2.0, "🍑": 2.0, "🥵": 1.7, "😈": 1.5, "🤬": 1.4,
    "😍": 1.4, "🤷‍♀️": 1.0, "❌": 1.2, "🚫": 1.2, "💀": 1.5, "👑": 1.1,
    "🤖": 1.3, "🤯": 1.7, "🤪": 1.7, "👼": 1.1, "💅": 1.9, "😜": 1.4, "😎": 1.2
}

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
        (slang_score * 0.6) +  # Slang has the most weight
        (emoji_score * 0.2) +  # Emojis contribute moderately
        (meme_score * 0.2) +   # Meme phrases have a similar impact to emojis
        (chaos_score * 0.1)    # Chaos contributes less for balance
    )
    return min(score * 100, 100)  # Cap at 100

def suggest_brainrotted_text(text, current_score):
    """Use OpenAI API to suggest edits for brainrotted text."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key is missing. Please set the OPENAI_API_KEY environment variable.")
    client = OpenAI(api_key=api_key)
    prompt = f"""
    You are an expert in analyzing and improving "brainrot" text scores based on a scoring algorithm. 
    Here is how the brainrot score works:

    **Brainrot Scoring System:**
    1. **Slang Density:** The use of specific slang words contributes the most to the score. Examples of slang: "skibidi," "rizz," "no cap," "based," "sigma," "gyatt."
    2. **Emoji Usage:** Emojis like "💀," "🤯," and "🥵" increase the score. Their impact is weighted based on their relevance to the slang or meme context.
    3. **Meme Phrases:** Recognizable meme phrases like "the ocky way," "whopper whopper whopper whopper," and "morbin time" boost the score.
    4. **Sentence Chaos:** Chaotic sentence structures with varying lengths and a mix of slang, memes, and emojis increase the score slightly.

    **Brainrot Words and Phrases:** 
    Single-word slang: {BRAINROT}
    Multi-word slang phrases: {BRAINROT_PHRASES}
    
    **Meme Phrases:**
    Meme phrases: {MEME_PHRASES}

    **User Input:**
    - Current Brainrot Score: {current_score}
    - Text to Improve: "{text}"

    **Your Task:**
    Based on the scoring system, provide suggestions to increase the brainrot score of the text. 
    Suggestions should:
    - Add relevant slang, meme phrases, and emojis to the text.
    - Suggest edits to increase sentence chaos without losing coherence.
    - Indicate which edits will have the biggest impact on the brainrot score.
    - Be concise and list out the suggestions, rather than rewriting the text entirely.

    Please return the suggestions in a list while also roasting the user for not being brainrotted enough in a brainrot manner.

    After giving the user suggestion, implement the suggestions to generate new text.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,  # Adjust for creativity
        max_tokens=700
    )
    return response.choices[0].message


if __name__ == "__main__":
    # Test Texts
    text1 = "top g comment team on the high key this a tuff comment no cap. Skibidi bop bop bop! sin city chill guy top g"
    text2 = "The quick brown fox jumps over the lazy dog multiple times, seeking adventure and excitement in a world filled with endless possibilities, where dreams are born, and limits are shattered. The fox encounters new challenges, faces obstacles, and learns valuable lessons about perseverance and courage. Along the way, the fox befriends a curious rabbit, a wise owl, and a playful squirrel, forming a team of unlikely adventurers who explore the mysteries of the forest together. Each step brings new discoveries, laughter, and moments of triumph. As the days turn to nights and seasons change, the fox grows stronger and wiser, cherishing the bonds formed and the experiences gained. The forest becomes a symbol of growth, a place where dreams flourish, and where the spirit of adventure never fades. This is the tale of a fox, a story of courage, friendship, and the beauty of a journey that lasts a lifetime, inspiring others to chase their own dreams and embrace the adventures that await."
    
    # Calculate scores
    score1 = refined_brainrot_score(text1)
    score2 = refined_brainrot_score(text2)
    brainrotted_text = suggest_brainrotted_text(text2, score2)

    print(f"Text 1 Brainrot Score: {score1}")
    print(f"Text 2 Brainrot Score: {score2}")
    print(f"{brainrotted_text.content}")

