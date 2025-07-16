import os
import json
import azure.cognitiveservices.speech as speechsdk
from threading import Event
from dotenv import load_dotenv
load_dotenv()

speech_key= os.getenv('SPEECH_KEY')
endpoint= os.getenv('speech_endpoint')
def transcribe_with_timestamps(audio_path):
    """
    Transcribes a Hindi WAV file using Azure Speech-to-Text and returns
    recognized text and word-level timestamps.
    """
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=endpoint)
    speech_config.speech_recognition_language = "hi-IN"  # "hi-IN" for hindi and "pa-IN" for punjabi
    speech_config.request_word_level_timestamps()
    speech_config.output_format = speechsdk.OutputFormat.Detailed

    audio_input = speechsdk.audio.AudioConfig(filename=audio_path)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_input
    )
  
    # Storage for results
    recognized_text = []
    chunks = []

    # Synchronization event
    done = Event()

    def recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detailed_json = evt.result.json
            detailed = json.loads(detailed_json)
            if 'NBest' in detailed and detailed['NBest']:
                nbest = detailed['NBest'][0]
                recognized_text.append(nbest.get('Display', ''))
                words = nbest.get('Words', [])
            else:
                recognized_text.append(detailed.get('DisplayText', ''))
                words = detailed.get('Words', [])
            for word_info in words:
                start = word_info['Offset'] / 10_000_000  # 100ns to seconds
                end = (word_info['Offset'] + word_info['Duration']) / 10_000_000
                chunks.append({'text': word_info['Word'], 'timestamp': (start, end)})

    def stop(evt):
        done.set()

    speech_recognizer.recognized.connect(recognized)
    speech_recognizer.session_stopped.connect(stop)
    speech_recognizer.canceled.connect(stop)

    speech_recognizer.start_continuous_recognition()
    done.wait()
    speech_recognizer.stop_continuous_recognition()

    if recognized_text:
        return {'text': ' '.join(recognized_text), 'chunks': chunks}
    else:
        return {'error': 'No recognized speech or error in recognition'}

# result = transcribe_hindi_with_timestamps(speech_key, endpoint, audio_path)
# print(result)
