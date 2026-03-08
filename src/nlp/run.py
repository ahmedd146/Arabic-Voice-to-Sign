from src.nlp.processor import ArSLProcessor
import arabic_reshaper
from bidi.algorithm import get_display

def print_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    bidi = get_display(reshaped)
    print(bidi)

def main():
    processor = ArSLProcessor()
    
    test_sentences = [
        "أريدُ أن أشربَ الماءَ",  # I want to drink water
        "السلامُ عليكم ورحمةُ اللهِ وبركاته", # Peace be upon you
        "كيفَ حالُكَ اليوم؟", # How are you today?
        "أنا ذاهبٌ إلى المدرسةِ" # I am going to school
    ]

    print("--- Arabic NLP Test ---")
    for sentence in test_sentences:
        print("\nOriginal:")
        print_arabic(sentence)
        
        # Process
        glosses = processor.process(sentence)
        
        print("Glosses (Keywords):")
        # Join list for display
        gloss_text = " | ".join(glosses)
        print_arabic(gloss_text)

if __name__ == "__main__":
    main()
