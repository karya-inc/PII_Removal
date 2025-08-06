import os
from pydub import AudioSegment

SUPPORTED_INPUT_FORMATS = ['.mp3', '.m4a', '.flac', '.aac', '.ogg', '.wma', '.mp2']

def convert_to_wav(file_path):
    file_name, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_INPUT_FORMATS:
        print(f"[Skipped] Unsupported format: {file_path}")
        return

    wav_file_path = f"{file_name}.wav"

    try:
        audio = AudioSegment.from_file(file_path)
        audio.export(wav_file_path, format="wav")
        print(f"[Converted] {file_path} → {wav_file_path}")
    except Exception as e:
        print(f"[Error] Failed to convert {file_path}: {e}")

def batch_convert_audio_to_wav(input_path):
    # Check if the input_path is a file or a directory
    if os.path.isfile(input_path):
        # Convert single file
        if input_path.lower().endswith('.wav'):
            print(f"[Skipped] Already a .wav file: {input_path}")
        else:
            convert_to_wav(input_path)
    elif os.path.isdir(input_path):
        # Process all files in the directory
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if not os.path.isfile(file_path):
                continue
            if file_path.lower().endswith('.wav'):
                continue
            convert_to_wav(file_path)
    else:
        print(f"[Error] Path not found: {input_path}")
