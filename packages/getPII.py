import os
import wave
import contextlib
# from packages.transcripts import transcribe_with_timestamps
from packages.getTranscript import process_asr
from packages.PII_detection import detect_pii_entities
from packages.mapTimeStamps import map_pii_to_timestamps
from packages.saveRedactedAudio import redact_audio

def process_audio_file(audio_path, output_folder, pii_categories=None, max_retries=15):
    """
    Processes a single audio file for PII:
      - Extracts metadata
      - Performs ASR (speech-to-text) with retries
      - Detects PII entities
      - Redacts PII segments
      - Returns summary info, and captures errors in 'error' field
    """
    if pii_categories is None:
        pii_categories = [
            'Person', 'PersonType', 'Organization', 'PhoneNumber',
            'Address', 'Location', 'BankAccountNumber'
        ]

    file_info = {
        "audio_path": audio_path,
        "duration_sec": None,
        "sample_rate": None,
        "channels": None,
        "channel_type": None,
        "PII_total": 0,
        "error": None  # To be set on errors
    }
    # For per-category PII counts
    file_category_map = {cat: 0 for cat in pii_categories}

    # ---- Audio Metadata Extraction ----
    if os.path.isfile(audio_path):
        try:
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
        except Exception as e:
            msg = f"Audio read: {e}"
            print(f"[Error] {msg}")
            file_info.update({
                "duration_sec": "Read error",
                "sample_rate": "Read error",
                "channels": "Read error",
                "channel_type": "Read error",
                "error": msg
            })
            return file_info
    else:
        msg = "Audio file not found"
        print(f"[Error] {msg}: {audio_path}")
        file_info.update({
            "duration_sec": "File not found",
            "sample_rate": "File not found",
            "channels": "File not found",
            "channel_type": "File not found",
            "error": msg
        })
        return file_info

    # ---- ASR Section with Retries ----
    asr_text, asr_timestamps = None, None
    try:
        for attempt in range(1, max_retries + 1):
            # transcript = transcribe_with_timestamps(audio_path)
            transcript = process_asr(audio_path)
            asr_text = transcript.get('text', '').strip()
            asr_timestamps = transcript.get('chunks', [])
            if asr_text and asr_timestamps:
                break
            if attempt < max_retries:
                print(f"[Retry {attempt}] ASR failed (missing text or timestamps) for {audio_path}. Retrying...")
            else:
                print(f"[Warning] Final ASR failed for {audio_path} after {max_retries} attempts.")
        if not asr_text or not asr_timestamps:
            msg = f"No ASR result for {audio_path}."
            print(f"[Warning] {msg} Skipping PII detection and redaction.")
            file_info["error"] = msg
            return file_info
    except Exception as e:
        msg = f"ASR exception: {e}"
        print(f"[Error] {msg}")
        file_info["error"] = msg
        return file_info

    # ---- PII Detection ----
    pii_words = []
    try:
        pii_result = detect_pii_entities([asr_text])
        for doc in pii_result:
            if hasattr(doc, "entities") and doc.entities:
                for entity in doc.entities:
                    if entity.confidence_score > 0.6 and entity.category in pii_categories:
                        pii_words.append(entity.text)
                        if entity.category in file_category_map:
                            file_category_map[entity.category] += 1
        file_info["PII_total"] = len(pii_words)
        file_info.update(file_category_map)
    except Exception as e:
        msg = f"PII detection failed: {e}"
        print(f"[Error] {msg}")
        file_info["error"] = msg

    # ---- Map PII and Redact Audio ----
    if asr_timestamps and pii_words:
        try:
            pii_segments = map_pii_to_timestamps(pii_words, asr_timestamps, threshold=0.6)
            redact_audio(audio_path, pii_segments, output_folder)
        except Exception as e:
            msg = f"Redaction failed: {e}"
            print(f"[Error] {msg}")
            file_info["error"] = msg
    else:
        if not pii_words:
            print(f"[Info] No PII detected for {audio_path}.")
        else:
            msg = f"No timestamps to map PII for {audio_path}. Skipping redaction."
            print(f"[Warning] {msg}")
            file_info["error"] = msg

    return file_info