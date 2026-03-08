from src.mapping.mapper import SignMapper
import arabic_reshaper
from bidi.algorithm import get_display

def print_arabic(text):
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        bidi = get_display(reshaped)
        print(bidi)
    except:
        print(text)

def main():
    print("--- Mapping System Test ---")
    # Verify the paths are correct relative to execution root
    mapper = SignMapper()
    
    # Test cases: Some from lexicon, some missing
    test_glosses = ["مرحبا", "محاضرة", "السلام", "عليكم", "اريد", "غير_موجود"]
    
    print(f"\nTesting Glosses: {test_glosses}")
    
    results = mapper.map_sentence(test_glosses)
    
    print("\nMapping Results:")
    for item in results:
        # Reshape for display
        try:
            display_gloss = get_display(arabic_reshaper.reshape(item['gloss']))
        except:
            display_gloss = item['gloss']

        if item['type'] == 'animation':
            print(f"✅ Found: {display_gloss} -> ID: {item['id']}")
        else:
            print(f"❌ Missing: {display_gloss}")

if __name__ == "__main__":
    main()
