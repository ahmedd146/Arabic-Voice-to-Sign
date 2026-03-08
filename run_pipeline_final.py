from src.asr.recognizer import ArabicSpeechRecognizer
from src.nlp.processor import ArSLProcessor
from src.mapping.mapper import SignMapper
import arabic_reshaper
from bidi.algorithm import get_display
import os
import time

def print_arabic(label, text):
    """
    Helper to print Arabic text correctly in Windows Terminal.
    """
    try:
        # Reshape the characters (connect letters)
        reshaped = arabic_reshaper.reshape(str(text))
        # Reorder for Bidi (Right-to-Left)
        bidi_text = get_display(reshaped)
        print(f"{label}: {bidi_text}")
        
    except Exception as e:
        print(f"{label}: {text} (Display Error: {e})")

def process_pipeline(audio_text, processor, mapper):
    """
    Executes the NLP and Mapping stages of the pipeline when new text is recognized.
    """
    if not audio_text:
        return
        
    print_arabic("\n1. Heard", audio_text)
    
    # --- STAGE 2: NLP PROCESSING ---
    glosses = processor.process(audio_text)
    gloss_str = " | ".join(glosses)
    print_arabic("2. Glosses", gloss_str)
    
    # --- STAGE 3: MAPPING TO ASSETS ---
    animation_sequence = mapper.map_sentence(glosses)
    
    print("3. Animation Sequence:")
    found_count = 0
    spell_count = 0
    for item in animation_sequence:
        if item['type'] == 'animation':
            print(f"   [PLAY] {item['id']} ({item['gloss']})")
            found_count += 1
        elif item['type'] == 'spell':
            print(f"      [SPELL] {item['id']} ({item['gloss']})")
            spell_count += 1
        elif item['type'] == 'missing_word_start':
            print(f"   [MISSING - FINGERSPELLING] {item['gloss']}")
        elif item['type'] == 'missing_word_end':
            pass # Just for logical grouping
            
    if found_count > 0 or spell_count > 0:
        print(f">> System would play {found_count} word animations and {spell_count} letter animations now.")
    else:
        print(">> No matching animations found in lexicon.")
        
    print("-" * 30)

def main():
    # Initialize Components
    print("Initializing System...")
    recognizer = ArabicSpeechRecognizer()
    processor = ArSLProcessor()
    mapper = SignMapper()
    
    print("\n" + "="*50)
    print("   ARABIC VOICE-TO-SIGN TRANSLATOR (PIPELINE)   ")
    print("="*50)
    print("Press Ctrl+C to exit.\n")
    
    # Callback function called whenever the recognizer finishes hearing a sentence
    def on_text_recognized(text):
        try:
            process_pipeline(text, processor, mapper)
        except Exception as e:
            print(f"\nError in pipeline processing: {e}")

    # Start continuous background listening
    recognizer.start_continuous(on_text_recognized)
    
    # Keep the main thread alive while background thread listens
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping continuous listening...")
        recognizer.stop_continuous()
        print("Exiting...")
        
if __name__ == "__main__":
    main()
