import torchaudio
import os

def redact_audio(audio_path, pii_segments, output_folder):
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"File not found: {audio_path}")

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get the original filename
    filename = os.path.basename(audio_path)
    output_path = os.path.join(output_folder, filename)

    # Filter valid segments
    valid_segments = [seg for seg in pii_segments if seg is not None]

    # Load audio
    waveform, sample_rate = torchaudio.load(audio_path)

    # Redact PII segments
    for start, end in valid_segments:
        start_sample = int(start * sample_rate)
        end_sample = int(end * sample_rate)
        waveform[:, start_sample:end_sample] = 0  # Silence

    # Save the redacted audio in the output folder with the same filename
    torchaudio.save(output_path, waveform, sample_rate)
    print(f"✅ Redacted audio saved at: {output_path}")

# Usage example:
# output_folder = r"D:\PII_Dataset\Redacted Audio"
# redact_audio(audio_path, pii_segments, output_folder)
