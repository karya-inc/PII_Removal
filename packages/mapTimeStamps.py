from difflib import SequenceMatcher

def preprocess_pii_words(pii_words_list):
    """
    Splits multi-word strings in a list of PII words into individual words.
    
    Args:
        pii_words_list (list): A list of strings, which may contain multi-word entities.
        
    Returns:
        list: A new list with all multi-word strings split into individual words.
    """
    preprocessed_list = []
    for word in pii_words_list:
        preprocessed_list.extend(word.split())
    return preprocessed_list

def map_pii_to_timestamps(pii_words, asr_chunks, threshold=0.6):
    """
    For each PII word (including repeats), find all its matches in asr_chunks.
    Returns a dictionary where each PII word is a key and its value is a list of all
    matching timestamps.
    """
    # Preprocess the pii_words list first
    preprocessed_pii_words = preprocess_pii_words(pii_words)

    # Create a dictionary with a list for each unique word from the preprocessed list
    pii_timestamps = []

    for word in preprocessed_pii_words:
        for chunk in asr_chunks:
            # Use SequenceMatcher to calculate a similarity ratio
            # Convert both strings to lowercase for case-insensitive matching
            score = SequenceMatcher(None, word.lower(), chunk['text'].lower()).ratio()
            
            # If the score is above the threshold, consider it a match
            if score >= threshold:
                pii_timestamps.append(chunk['timestamp'])

    return pii_timestamps

def map_pii_to_timestamps_with_words(pii_words, asr_chunks, threshold=0.6):
    """
    For each PII word (including repeats), find all its matches in asr_chunks.
    Returns a dictionary where each PII word is a key and its value is a list of all
    matching timestamps.
    """
    # Preprocess the pii_words list first
    preprocessed_pii_words = preprocess_pii_words(pii_words)

    # Create a dictionary with a list for each unique word from the preprocessed list
    pii_timestamps = {word: [] for word in set(preprocessed_pii_words)}

    for word in preprocessed_pii_words:
        for chunk in asr_chunks:
            # Use SequenceMatcher to calculate a similarity ratio
            # Convert both strings to lowercase for case-insensitive matching
            score = SequenceMatcher(None, word.lower(), chunk['text'].lower()).ratio()
            
            # If the score is above the threshold, consider it a match
            if score >= threshold:
                pii_timestamps[word].append(chunk['timestamp'])

    return pii_timestamps

# --- Example Usage ---

if __name__ == '__main__':
    # Original PII list with a multi-word entity
    original_pii_words = ['दीपा', 'दीदी', 'संगीता वर्मा']

    # ASR chunks with fuzzy matches and a multi-word name
    asr_chunks = [
        {'text': "नमस्ते दीपा", 'timestamp': (0.71, 1.03)},
        {'text': "मेरी बहन दीदी", 'timestamp': (7.43, 7.67)},
        {'text': "यहां पर हैं संगीता वर्मा", 'timestamp': (11.75, 12.5)},
        {'text': "यह दीदी के घर है", 'timestamp': (41.11, 41.47)},
    ]

    # Find all timestamps for the PII words
    all_pii_timestamps = map_pii_to_timestamps(original_pii_words, asr_chunks, threshold=0.8)

    print(f"Original PII list: {original_pii_words}")
    print("\n--- All Timestamps for PII words ---")
    for pii, timestamps in all_pii_timestamps.items():
        print(f"'{pii}': {timestamps}")