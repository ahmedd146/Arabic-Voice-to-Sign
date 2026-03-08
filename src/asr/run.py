from src.asr.recognizer import ArabicSpeechRecognizer
import arabic_reshaper
from bidi.algorithm import get_display

def main():
    recognizer = ArabicSpeechRecognizer()
    
    print("--- Arabic ASR Test (Continuous) ---")
    print("Press Ctrl+C to exit")
    
    def on_text(text):
        if text:
            try:
                # Correct text for console display
                reshaped_text = arabic_reshaper.reshape(text)
                bidi_text = get_display(reshaped_text)
                print(f"\nFinal Result: {bidi_text}")
            except Exception as e:
                print(f"Display Error: {e}")

    recognizer.start_continuous(on_text)
    
    import time
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping continuous listening...")
        recognizer.stop_continuous()
        print("Exiting...")

if __name__ == "__main__":
    main()
