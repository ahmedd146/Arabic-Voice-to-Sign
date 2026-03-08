import speech_recognition as sr

class ArabicSpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.stop_listening_fn = None

    def listen(self):
        """
        Synchronous (blocking) listen.
        Listens to the microphone and returns the recognized Arabic text.
        Returns None if no speech is detected or if there is an error.
        """
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now (Arabic).")
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio, language="ar-AR")
                return text

            except sr.WaitTimeoutError:
                print("Listening timed out while waiting for phrase to start")
                return None
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return None
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return None

    def start_continuous(self, text_callback):
        """
        Starts Voice Activity Detection (VAD) based listening in the background.
        When a phrase is detected, it is recognized and passed to text_callback.
        """
        import webrtcvad
        import pyaudio
        import threading
        import collections

        self.vad = webrtcvad.Vad(3) # Aggressiveness from 0 to 3
        
        # Audio formatting required by webrtcvad
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000 # 16kHz
        CHUNK_DURATION_MS = 30 # WebRTC VAD requires 10, 20, or 30 ms frames
        CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)
        
        # Config for recognizing a phrase
        NUM_PADDING_CHUNKS = int(300 / CHUNK_DURATION_MS) # 300ms of padding
        NUM_WINDOW_CHUNKS = int(400 / CHUNK_DURATION_MS)  # 400ms window to detect speech start
        NUM_WINDOW_CHUNKS_END = int(600 / CHUNK_DURATION_MS) # 600ms of silence to trigger end
        
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=FORMAT,
                                   channels=CHANNELS,
                                   rate=RATE,
                                   input=True,
                                   start=False,
                                   frames_per_buffer=CHUNK_SIZE)
        
        self.stop_event = threading.Event()
        
        def vad_record_loop():
            self.stream.start_stream()
            print("Microphone is live (VAD Active)... Speak naturally. (Press Ctrl+C to stop)")
            
            ring_buffer = collections.deque(maxlen=NUM_PADDING_CHUNKS)
            triggered = False
            voiced_frames = []
            
            # For detecting start of speech
            window_ring_buffer = collections.deque(maxlen=NUM_WINDOW_CHUNKS)
            # For detecting end of speech
            silence_ring_buffer = collections.deque(maxlen=NUM_WINDOW_CHUNKS_END)

            while not self.stop_event.is_set():
                try:
                    chunk = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    is_speech = self.vad.is_speech(chunk, RATE)
                except Exception as e:
                    print(f"Audio read error: {e}")
                    break
                
                if not triggered:
                    ring_buffer.append((chunk, is_speech))
                    window_ring_buffer.append(is_speech)
                    
                    # If enough chunks in window are speech, trigger recording
                    num_voiced = sum(window_ring_buffer)
                    if num_voiced > 0.9 * NUM_WINDOW_CHUNKS:
                        triggered = True
                        for f, s in ring_buffer:
                            voiced_frames.append(f)
                        window_ring_buffer.clear()
                        silence_ring_buffer.clear()
                        # print("\n[VAD] Speech started...")
                else:
                    voiced_frames.append(chunk)
                    silence_ring_buffer.append(is_speech)
                    
                    # If enough chunks in window are silence, stop recording
                    num_unvoiced = len(silence_ring_buffer) - sum(silence_ring_buffer)
                    if num_unvoiced > 0.9 * NUM_WINDOW_CHUNKS_END:
                        # print("[VAD] Speech ended. Processing...")
                        triggered = False
                        
                        # Process the collected frames
                        audio_data = b''.join(voiced_frames)
                        # We turn the raw PCM data into a SpeechRecognition AudioData object
                        audio = sr.AudioData(audio_data, RATE, 2) # sample width 2 for paInt16
                        
                        # Process using google in a sub-thread to not block the VAD loop
                        threading.Thread(target=self._process_audio, args=(audio, text_callback)).start()
                        
                        voiced_frames = []
                        ring_buffer.clear()
                        silence_ring_buffer.clear()
            
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()

        self.listen_thread = threading.Thread(target=vad_record_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
    def _process_audio(self, audio, text_callback):
        try:
            text = self.recognizer.recognize_google(audio, language="ar-AR")
            if text:
                text_callback(text)
        except sr.UnknownValueError:
            pass # Ignore silence/noise that couldn't be recognized
        except sr.RequestError as e:
            print(f"\n[ASR Error] Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print(f"\n[ASR Error] An unexpected error occurred: {e}")

    def stop_continuous(self):
        """
        Stops the VAD background listening if it is active.
        """
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
            if hasattr(self, 'listen_thread'):
                self.listen_thread.join()
            print("Stopped VAD background listening.")
