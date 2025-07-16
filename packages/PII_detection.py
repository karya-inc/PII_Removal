import os
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()
language_key= os.getenv('LANGUAGE_KEY')
language_endpoint= os.getenv('language_endpoint')

def authenticate_client():
    ta_credential = AzureKeyCredential(language_key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=language_endpoint,
            credential=ta_credential)
    return text_analytics_client

def pii_recognition_example(client, documents):
    response = client.recognize_pii_entities(documents, language="hi")  # hi for hindi and pa for punjabi
    result = [doc for doc in response if not doc.is_error]
    return result

def detect_pii_entities(documents):
    client = authenticate_client()
    return pii_recognition_example(client, documents)

# Example usage:
# asr_text = [result['text']]  # Use your ASR output text here
# pii_words = pii_recognition_example(client, asr_text)