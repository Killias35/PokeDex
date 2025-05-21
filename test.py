import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Mot à détecter
MOT_CLE = "arrête"

# Charge le modèle Vosk
model = Model("vosk-model-fr-0.22")

# Initialisation du micro
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

# Reconnaissance
rec = KaldiRecognizer(model, 16000)
rec.SetWords(True)

# Stream audio
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("Parle maintenant. Ctrl+C pour quitter.")
    try:
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                texte = result.get("text", "").lower()
                print("Reconnu :", texte)

                if MOT_CLE in texte:
                    print(f">>> Mot clé détecté : {MOT_CLE} <<<")

            else:
                # Optionnel : partiel en temps réel
                partiel = json.loads(rec.PartialResult())
                print("Partiel :", partiel.get("partial", ""), end="\r")

    except KeyboardInterrupt:
        print("\nFin de l'écoute.")
