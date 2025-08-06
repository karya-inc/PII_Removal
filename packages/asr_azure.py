import os
import json
from sre_constants import IN
import requests

# # ==================
# # Azure Configuration
# # ==================

# API_KEY = "YOUR_AZURE_SPEECH_API_KEY"
# ENDPOINT = "https://<your-region>.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
# LANGUAGE = "hi-IN"  # Use "pa-IN", "en-IN" etc. as needed

# # ==================
# # Batch Parameters
# # ==================

# INPUT_FOLDER = "audio"         # 🎧 Folder containing WAV files
# OUTPUT_FOLDER = "transcripts"  # 📄 Folder to save JSONs
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==================
# Azure Transcription Function
# ==================

def transcribe_with_word_offsets(audio_path, API_KEY=None, ENDPOINT=None, LANGUAGE="hi-IN"):
    headers = {
        "Ocp-Apim-Subscription-Key": API_KEY,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json"
    }

    params = {
        "language": LANGUAGE,
        "format": "detailed",
        "enableWordTimeOffsets": "true"  # 🔑 Required for word-level timestamps
    }

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    print(f"🔁 Sending: {os.path.basename(audio_path)}")
    response = requests.post(ENDPOINT, headers=headers, params=params, data=audio_data)

    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} → {response.text}")
        return None

    try:
        res = response.json()
        nbest = res.get("NBest", [{}])[0]
        display = nbest.get("Display", "")
        words = nbest.get("Words", [])

        chunks = []
        for word in words:
            start = round(word["Offset"] / 10_000_000, 2)
            end = round((word["Offset"] + word["Duration"]) / 10_000_000, 2)
            chunks.append({
                "text": word["Word"],
                "timestamp": (start, end)
            })

        return {
            "text": display,
            "chunks": chunks
        }

    except Exception as e:
        print("❌ Error parsing response:", str(e))
        return None

# ==================
# Batch Execute
# ==================

def batch_transcribe(INPUT_FOLDER, OUTPUT_FOLDER="transcripts", API_KEY=None, ENDPOINT=None):
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".wav")]
    print(f"\n🎧 Found {len(files)} audio files.")

    for i, file_name in enumerate(files, 1):
        full_path = os.path.join(INPUT_FOLDER, file_name)
        base_name = os.path.splitext(file_name)[0]
        output_path = os.path.join(OUTPUT_FOLDER, base_name + ".json")

        result = transcribe_with_word_offsets(full_path, API_KEY, ENDPOINT)

        if result:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved: {output_path}")
        else:
            print(f"⚠️ Skipped (error): {file_name}")

# # Run the batch job
# if __name__ == "__main__":
#     batch_transcribe(INPUT_FOLDER)
