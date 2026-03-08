import pyarabic.araby as araby
import nltk
import re
from nltk.corpus import stopwords
try:
    import qalsadi.lemmatizer
    has_qalsadi = True
except ImportError:
    has_qalsadi = False

# Ensure NLTK data is downloaded (this might need to be run once manually if it fails, 
# but we'll try to handle it gracefully or use a fallback)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ArSLProcessor:
    def __init__(self):
        # 1. Load NLTK stopwords
        raw_stopwords = set(stopwords.words('arabic'))
        
        # 2. Add custom stopwords (prepositions/particles)
        custom_stops = {
            "أن", "لن", "من", "إلى", "عن", "على", "في", "ب", "ك", "ل", 
            "التي", "الذي", "الذين", "هذا", "هذه", "ذلك", "ما", "يا", "هل"
        }
        raw_stopwords.update(custom_stops)

        # 3. Define Whitelist (Critical words that must NEVER be removed)
        # Includes question words, pronouns, and negation
        self.whitelist = {
            "كيف", "أين", "متى", "كم", "لماذا", "من", # Questions (Caution: 'من' can be 'from' or 'who')
            "أنا", "أنت", "هو", "هي", "نحن", "هم", "أنتم", # Pronouns
            "لا", "لم", "ليس", "لن",                  # Negation
            "غدا", "أمس", "اليوم", "الآن"             # Time words
        }

        # 4. Normalize everything to match the input normalization
        self.stop_words = set()
        for word in raw_stopwords:
            self.stop_words.add(self.normalize_text(word))
            
        self.whitelist_norm = set()
        # Remove whitelisted words from the stoplist ensuring they are normalized too
        for word in self.whitelist:
            norm_word = self.normalize_text(word)
            self.whitelist_norm.add(norm_word)
            if norm_word in self.stop_words:
                self.stop_words.remove(norm_word)
                
        # 5. Initialize Lemmatizer
        if has_qalsadi:
            self.lemmatizer = qalsadi.lemmatizer.Lemmatizer()
        else:
            self.lemmatizer = None

    def normalize_text(self, text):
        """Removes diacritics, tatweel, and standardizes Alef/Hamza."""
        text = araby.strip_tashkeel(text)
        text = araby.strip_tatweel(text)
        # Using araby.normalize_alef can turn ى into ا in some edge cases. We might want to keep it simple.
        # But we will leave it for now.
        # Removed text = re.sub(r'\bال', '', text) because it breaks words like "المدرسة", "إلى", etc. Qalsadi handles "ال".
        text = text.replace('ة', 'ه') # Standardize Teh Marbuta to Heh
        return text

    def tokenize(self, text):
        """Splits text into words."""
        return araby.tokenize(text)

    def remove_stopwords(self, tokens):
        """Removes non-essential words for Sign Language, respecting the whitelist."""
        filtered = []
        for word in tokens:
            if word in self.stop_words:
                continue
            filtered.append(word)
        return filtered
        
    def lemmatize(self, tokens):
        """Extracts the root/lemma of Arabic words (e.g. الكتب -> كتاب)"""
        if not self.lemmatizer:
            return tokens
            
        lemmatized_tokens = []
        for word in tokens:
            # Skip short words and direct whitelist hits
            if len(word) <= 2 or word in self.whitelist_norm:
                lemmatized_tokens.append(word)
                continue
                
            try:
                lemma = self.lemmatizer.lemmatize(word)
                # Fallback if lemma isn't found or is weirdly processed
                if not lemma or len(lemma) < 2:
                    lemma = word
                lemmatized_tokens.append(lemma)
            except Exception:
                lemmatized_tokens.append(word)
                
        return lemmatized_tokens
        
    def reorder_grammar(self, tokens):
        """
        Reorders Arabic (VSO) into ArSL (Usually SOV or Topic-Comment).
        This is a basic heuristic approach without deep dependency parsing.
        """
        if len(tokens) < 3:
            return tokens
            
        # Heuristic: Find common structure (Verb Subject Object) -> (Subject Object Verb)
        # e.g. "أريد أنا قلم" -> "أنا قلم أريد"
        # Since we just lemmatized, identifying exact parts of speech is tricky without a full parser like CamelTools
        # We will do a basic swap if the sentence starts with a known verb.
        
        # In a production system, we'd use POS tagging (Part of Speech).
        # For now, let's implement a pseudo-reordering based on pronouns and question words.
        
        reordered = []
        questions = []
        time_words = []
        subjects = []
        verbs_objects = []
        
        time_lexicon = ["امس", "غدا", "اليوم", "الان", "بعدين"]
        
        for word in tokens:
            if word in ["كيف", "اين", "متى", "كم", "لماذا"]:
                questions.append(word)
            elif word in time_lexicon:
                time_words.append(word)
            elif word in ["انا", "انت", "هو", "هي", "نحن", "هم", "انتم"]:
                subjects.append(word)
            else:
                verbs_objects.append(word)
                
        # Basic ArSL order: Time -> Subject -> Object/Verb -> Question
        reordered.extend(time_words)
        reordered.extend(subjects)
        reordered.extend(verbs_objects)
        reordered.extend(questions) # Questions often go at the end in ArSL
        
        return reordered

    def process(self, text):
        """
        Full pipeline: Normalize -> Tokenize -> Lemmatize -> Stopwords -> Reorder Grammar
        Returns a list of 'glosses' (keywords).
        """
        normalized = self.normalize_text(text)
        tokens = self.tokenize(normalized)
        lemmas = self.lemmatize(tokens)
        glosses = self.remove_stopwords(lemmas)
        
        # Apply grammar reordering rules for Arabic Sign Language
        ordered_glosses = self.reorder_grammar(glosses)
        
        # Final pass over normalizer to ensure lemmas didn't introduce new un-normalized chars
        final_glosses = []
        for g in ordered_glosses:
            if not g.strip():
                continue
            # Safely remove definite article "ال" if the word is long enough
            # to avoid breaking words like "الى" (to), "العاب" (games), "الوان" (colors).
            if g.startswith("ال") and len(g) > 4 and g not in self.whitelist_norm:
                g = g[2:]
            final_glosses.append(self.normalize_text(g))
        
        return final_glosses
