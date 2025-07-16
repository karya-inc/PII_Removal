import os
import wave
import contextlib
from packages.transcripts import transcribe_with_timestamps
from packages.PII_detection import detect_pii_entities
from packages.mapTimeStamps import map_pii_to_timestamps
from packages.saveRedactedAudo import redact_audio

def process_audio_file(audio_path, output_folder, pii_categories=None):
    if pii_categories is None:
        pii_categories = ['Person','PersonType', 'Organization', 'PhoneNumber', 'Address', 'Location', 'PhoneNumber', 'BankAccountNumber']

    file_info = {
        "audio_path": audio_path,
        "duration_sec": None,
        "sample_rate": None,
        "channels": None,
        "channel_type": None,
        "PII_total": 0
    }
    # Per-file category count
    file_category_map = {cat: 0 for cat in pii_categories}

    if os.path.isfile(audio_path):
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration_sec = frames / float(rate)
            channels = f.getnchannels()
            channel_type = "Mono" if channels == 1 else "Dual" if channels == 2 else "Other"
            file_info.update({
                "duration_sec": duration_sec,
                "sample_rate": rate,
                "channels": channels,
                "channel_type": channel_type
            })
    else:
        file_info.update({
            "duration_sec": "File not found",
            "sample_rate": "File not found",
            "channels": "File not found",
            "channel_type": "File not found"
        })
        return file_info

    # --- PII Workflow ---
    transcript = transcribe_with_timestamps(audio_path)
    asr_text = transcript.get('text', '')
    pii_result = detect_pii_entities([asr_text])
    pii_words = []
    for doc in pii_result:
        for entity in doc.entities:
            if hasattr(entity, 'confidence_score') and entity.confidence_score > 0.6 and entity.category in pii_categories:
                pii_words.append(entity.text)
                file_category_map[entity.category] += 1
    file_info["PII_total"] = len(pii_words)
    file_info.update(file_category_map)
    pii_segments = map_pii_to_timestamps(pii_words, transcript['chunks'], threshold=0.6)
    redact_audio(audio_path, pii_segments, output_folder)
    return file_info