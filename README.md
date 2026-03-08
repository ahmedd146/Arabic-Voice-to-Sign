# Arabic Voice-to-Sign Translator

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A real-time system that translates spoken Modern Standard Arabic (MSA) into Arabic Sign Language (ArSL) glosses and maps them to animation assets.

## Project Structure
- `src/asr/`: **Automatic Speech Recognition** (converts Mic -> Text).
- `src/nlp/`: **Natural Language Processing** (Text -> Simplified Glosses).
- `src/mapping/`: **Mapping System** (Glosses -> Animation IDs).
- `dataset/sign_lexicon/`: Contains the JSON dictionary (`galala_arsl.json`).

## Requirements
- Python 3.10+
- Internet connection (for Google Speech API)
- Microphone

## Installation
```bash
pip install -r requirements.txt
```

## How to Run
To start the full integrated pipeline:

```bash
python run_pipeline_final.py
```

### Other Utilities
- `run_asr.py`: Test microphone and speech recognition only.
- `run_nlp.py`: Test text processing logic.
- `run_mapping.py`: Test dictionary lookups.

## Features
- **Visual Correction**: Automatically fixes Arabic text display in Windows Terminals (RTL/Joining).
- **Stopword Filtering**: Removes grammar particles not used in ArSL.
- **Whitelist**: Preserves critical Sign Language terms (Who, Where, I, You, etc.).
