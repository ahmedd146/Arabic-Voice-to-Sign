from src.nlp.processor import ArSLProcessor
import json
import os

class SignMapper:
    def __init__(self, lexicon_path=None):
        if lexicon_path is None:
            # Default to the Galala Lexicon in the dataset folder
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.lexicon_path = os.path.join(base_dir, 'dataset', 'sign_lexicon', 'galala_arsl.json')
        else:
            self.lexicon_path = lexicon_path
            
        self.normalizer = ArSLProcessor()
        self.lexicon = {}
        self.load_lexicon()
        
        # Mapping for Arabic alphabet to sign animations for fingerspelling fallback
        self.alphabet_mapping = {
            'ا': 'alef.anim', 'ب': 'baa.anim', 'ت': 'taa.anim', 'ث': 'thaa.anim',
            'ج': 'jeem.anim', 'ح': 'haa.anim', 'خ': 'khaa.anim', 'د': 'daal.anim',
            'ذ': 'thaal.anim', 'ر': 'raa.anim', 'ز': 'zaay.anim', 'س': 'seen.anim',
            'ش': 'sheen.anim', 'ص': 'saad.anim', 'ض': 'daad.anim', 'ط': 'taa_letter.anim',
            'ظ': 'dhaa.anim', 'ع': 'ayn.anim', 'غ': 'ghayn.anim', 'ف': 'faa.anim',
            'ق': 'qaaf.anim', 'ك': 'kaaf.anim', 'ل': 'laam.anim', 'م': 'meem.anim',
            'ن': 'noon.anim', 'ه': 'haa_letter.anim', 'و': 'waaw.anim', 'ي': 'yaa.anim',
            # Adding normalized/variations
            'أ': 'alef.anim', 'إ': 'alef.anim', 'آ': 'alef.anim', 'ة': 'haa_letter.anim',
            'ى': 'yaa.anim', 'ؤ': 'waaw.anim', 'ئ': 'yaa.anim', 'ء': 'hamza.anim'
        }

    def load_lexicon(self):
        """Loads the JSON lexicon into memory and normalizes keys."""
        try:
            with open(self.lexicon_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                raw_lexicon = data.get('lexicon', {})
                
                # Normalize keys for robust lookup
                for key, value in raw_lexicon.items():
                    norm_key = self.normalizer.normalize(key)
                    self.lexicon[norm_key] = value
                    
            print(f"Loaded Lexicon with {len(self.lexicon)} entries.")
        except FileNotFoundError:
            print(f"Error: Lexicon file not found at {self.lexicon_path}")
            self.lexicon = {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in lexicon file at {self.lexicon_path}")
            self.lexicon = {}

    def get_animation_id(self, gloss):
        """
        Searches for a gloss in the lexicon.
        Returns the 'sign_id' (or 'animation' filename) if found, else None.
        """
        # Normalize the input gloss to match lexicon keys
        norm_gloss = self.normalizer.normalize(gloss)
        
        # Exact match on normalized key
        if norm_gloss in self.lexicon:
            return self.lexicon[norm_gloss].get('sign_id')
        
        return None

    def map_sentence(self, glosses):
        """
        Maps a list of glosses to a list of animation IDs.
        Retains original gloss if no animation is found (so we know what's missing).
        """
        mapped_sequence = []
        for gloss in glosses:
            anim_id = self.get_animation_id(gloss)
            
            if anim_id:
                mapped_sequence.append({"type": "animation", "id": anim_id, "gloss": gloss})
            else:
                # Missing sign - Finger spelling fallback
                mapped_sequence.append({"type": "missing_word_start", "gloss": gloss})
                for char in gloss:
                    if char in self.alphabet_mapping:
                        mapped_sequence.append({
                            "type": "spell", 
                            "id": self.alphabet_mapping[char], 
                            "gloss": char,
                            "original_word": gloss
                        })
                mapped_sequence.append({"type": "missing_word_end", "gloss": gloss})
        
        return mapped_sequence
