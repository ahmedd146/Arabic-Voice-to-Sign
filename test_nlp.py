import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())

from src.nlp.processor import ArSLProcessor
import pyarabic.araby as araby

p = ArSLProcessor()

text = "متى نذهب نحن إلى المدرسة غداً؟"
normalized = p.normalize_text(text)
print("Normalized:", normalized)

tokens = p.tokenize(normalized)
print("Tokens:", tokens)

lemmas = p.lemmatize(tokens)
print("Lemmas:", lemmas)

print("غدا in stopwords?", p.normalize_text("غدا") in p.stop_words)
print("غدا in whitelist?", p.normalize_text("غدا") in p.whitelist)

glosses = p.remove_stopwords(lemmas)
print("Glosses post-stopwords:", glosses)

ordered = p.reorder_grammar(glosses)
print("Ordered:", ordered)
