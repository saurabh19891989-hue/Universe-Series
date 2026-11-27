"""Chatterbox-Turbo CPU speed probe (what was run). venv (py3.13): pip install chatterbox-tts "setuptools<81" soundfile
Needed local patches on py3.13/numpy2: cast librosa audio/mels to float32 (s3tokenizer.py log_mel / voice_encoder.inference).
Result on shared 4-core box (load avg 8-9): ~270 s to render 3.1 s of speech (RTF ~90) -> unusable. Original Chatterbox: 279 s for 2.7 s."""
import time, sys
from chatterbox.tts_turbo import ChatterboxTurboTTS
m = ChatterboxTurboTTS.from_pretrained('cpu')
t = time.time(); w = m.generate('The crater is present. The address has been withdrawn.', audio_prompt_path=sys.argv[1])
print('seconds', time.time()-t, 'audio_seconds', w.shape[1]/m.sr)
