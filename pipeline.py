
from packages.getTranscript import process_asr
from packages.PII_detection import detect_pii_entities
from packages.mapTimeStamps import map_pii_to_timestamps
from packages.saveRedactedAudo import redact_audio

input_audio_path = r"inputs\in-70001-919417328881-20250530-160219-1748601139.42162.wav"

transcript = process_asr(input_audio_path)

print(transcript)

asr_text = [transcript['text']]
pii_result = detect_pii_entities(asr_text)
pii_words = []
for doc in pii_result:
    print("Redacted Text: {}".format(doc.redacted_text))
    for entity in doc.entities:
        if entity.confidence_score > 0.7 and entity.category in  ['Person', 'Organization', 'PhoneNumber', 'Address', 'Location', 'PhoneNumber', 'BankAccountNumber']:
            print("Entity: {}".format(entity.text))
            pii_words.append(entity.text)
            print("\tCategory: {}".format(entity.category))
            print("\tConfidence Score: {}".format(entity.confidence_score))
            print("\tOffset: {}".format(entity.offset))
            print("\tLength: {}".format(entity.length))
print(pii_words)


pii_segments = map_pii_to_timestamps(pii_words, transcript['chunks'], threshold=0.5)
print(pii_segments)

redact_audio(input_audio_path,pii_segments, output_folder="output_audio")