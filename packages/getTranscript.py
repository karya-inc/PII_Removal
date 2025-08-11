import json
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Constants - keep your URL, API key, headers, and payload separate
API_URL = os.getenv("API_URL_LANGUAGE_SERVER")
API_KEY = os.getenv("API_KEY_LANGUAGE_SERVER")

HEADERS = {
    "accept": "application/json",
    "X-API-Key": API_KEY,
}

PAYLOAD_DATA = {
    "user_email": "pallavi.sahu@karya.in",
    "project_name": "Individual",
    "task_type": "Batch",
    "language_identification": False,
    "metadata": {"priority": "high"},
    "description": "It's used to separate PII entities from the ASR transcripts of audio samples.",
    "locale": "hi-IN",
    "provider": "AZURE",
    "models": ["long"],
}



def submit_transcription(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        files = {
            "files": ("audio.wav", audio_file, "audio/wav"),
        }
        # Pass payload_data as a string field in 'data' parameter (not files)
        data = {
            "payload_data": json.dumps(PAYLOAD_DATA)
        }

        response = requests.post(API_URL, headers=HEADERS, files=files, data=data)

    print("Status code:", response.status_code)
    try:
        print("Response JSON:", response.json())
        return response.json()
    except Exception:
        print("Response text:", response.text)
        return None


def poll_status(task_id, wait_seconds=30, max_retries=30):
    status_url = f"https://language-server-main-306601896586.us-central1.run.app/v1/status/{task_id}"
    for attempt in range(max_retries):
        response = requests.get(status_url, headers=HEADERS)
        print(f"Polling attempt {attempt+1}, Status Code:", response.status_code)
        if response.status_code != 200:
            print("Error getting status:", response.text)
            return None
        data = response.json()
        status = data.get("status")
        print("Current status:", status)
        if status == "COMPLETED":
            return data
        elif status in ["FAILED", "CANCELLED"]:
            print(f"Task ended with status: {status}")
            return None
        time.sleep(wait_seconds)
    print("Max retries reached without completion.")
    return None


def extract_asr_transcript(data):
    # This assumes the data structure from the response JSON contains an 'responses' list.
    # Each response's 'output' contains 'transcriptions' which include 'recognizedPhrases' → list of phrases with words.
    responses = data.get("responses", [])
    if not responses:
        print("No responses found in data.")
        return None

    transcriptions = responses[0].get("response", {}).get("output", {}).get("transcriptions", [])
    if not transcriptions:
        print("No transcriptions found.")
        return None

    # Extract all word-level chunks with text and timestamps
    words_chunks = []
    for transcription in transcriptions:
        recognizedPhrases = transcription.get("recognizedPhrases", [])
        for phrase in recognizedPhrases:
            # 'nBest' is a list of hypotheses; we use the first one (best)
            nbest = phrase.get("nBest", [])
            if not nbest:
                continue
            best_hypo = nbest[0]
            words = best_hypo.get("words", [])
            for w in words:
                # Each word dict should have 'word', 'offsetMilliseconds', 'durationMilliseconds'
                text = w.get("word")
                start_ms = w.get("offsetMilliseconds")  # int, milliseconds
                dur_ms = w.get("durationMilliseconds")
                if text is None or start_ms is None or dur_ms is None:
                    continue
                start_s = start_ms / 1000.0
                end_s = (start_ms + dur_ms) / 1000.0
                words_chunks.append({
                    "text": text,
                    "timestamp": (start_s, end_s)
                })

    # Aggregate full text by joining word texts with space (adjust if ASR text needs special handling)
    full_text = " ".join(chunk["text"] for chunk in words_chunks)

    transcript = {
        "text": full_text,
        "chunks": words_chunks
    }

    return transcript

def process_asr(audio_path):
    response = submit_transcription(audio_path)
    if not response:
        print("Failed to submit transcription.")
        return

    task_id = response.get("task_id")  # directly get task_id from returned dictionary
    if not task_id:
        print("Failed to retrieve task ID from response.")
        return

    print(f"Submitted transcription task. Task ID: {task_id}")
    print("Polling for completion...")

    result_data = poll_status(task_id)
    if not result_data:
        print("Failed to get transcription result or task did not complete.")
        return

    transcript = extract_asr_transcript(result_data)
    return transcript
    # if not transcript:
    #     print("Failed to extract transcript.")
    #     return

    # # Print/output transcript JSON with word-level timestamps
    # print("\nFinal Transcript JSON:")
    # print(json.dumps(transcript, ensure_ascii=False, indent=2))



if __name__ == "__main__":
    process_asr()
