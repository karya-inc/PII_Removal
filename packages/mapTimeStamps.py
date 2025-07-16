from difflib import SequenceMatcher

def map_pii_to_timestamps(pii_words, asr_chunks, threshold=0.6):
    """
    For each PII word (including repeats), find its N-th best match in asr_chunks.
    Returns a list of timestamps, one for each PII word, in order.
    """
    timestamps = []
    used = [False] * len(asr_chunks)  # Track which chunks have been matched

    for word in pii_words:
        best_idx = None
        best_score = 0
        for idx, chunk in enumerate(asr_chunks):
            if used[idx]:
                continue  # Don't reuse a chunk
            score = SequenceMatcher(None, word, chunk['text']).ratio()
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx is not None and best_score >= threshold:
            timestamps.append(asr_chunks[best_idx]['timestamp'])
            used[best_idx] = True  # Mark this chunk as used
        else:
            timestamps.append(None)  # No match found for this word
    return timestamps

# Usage:
# asr_chunks = result['chunks']
# pii_segments = map_pii_to_timestamps(pii_words, asr_chunks)

# print(pii_segments)