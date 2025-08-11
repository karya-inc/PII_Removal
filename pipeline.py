from packages.getTranscript import process_asr
from packages.PII_detection import detect_pii_entities
from packages.mapTimeStamps import map_pii_to_timestamps
from packages.saveRedactedAudio import redact_audio

def main():
    input_audio_path = r"inputs\in-70001-919417328881-20250530-160219-1748601139.42162.wav"

    # Step 1: Transcribe audio
    transcript = process_asr(input_audio_path)

    # Step 2: Detect PII entities
    asr_text = [transcript['text']]
    if not asr_text:
        print("No text found in transcript.")
        return
    pii_result = detect_pii_entities(asr_text)
    pii_words = [
        entity.text
        for doc in pii_result
        for entity in doc.entities
        if entity.confidence_score > 0.7 and entity.category in {
            'Person', 'Organization', 'PhoneNumber', 'Address',
            'Location', 'BankAccountNumber'
        }
    ]
    print(pii_words)

    # Step 3: Map PII words to timestamps
    pii_segments = map_pii_to_timestamps(
        pii_words, transcript['chunks'], threshold=0.5
    )

    # Step 4: Redact audio
    redact_audio(input_audio_path, pii_segments, output_folder="output_audio")

if __name__ == "__main__":
    main()
