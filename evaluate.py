
from packages.transcripts import transcribe_with_timestamps
from packages.PII_detection import detect_pii_entities
from packages.mapTimeStamps import map_pii_to_timestamps, map_pii_to_timestamps_with_words
import os
import json


input_audio_path = r"D:\Coding\PII Evaluation\main server dataset\phase 3\4547022.wav"


transcript = transcribe_with_timestamps(input_audio_path)
# print(transcript)


asr_text = [transcript['text']]
pii_result = detect_pii_entities(asr_text)
pii_words = []
for doc in pii_result:
    # print("Redacted Text: {}".format(doc.redacted_text))
    for entity in doc.entities:
        if entity.confidence_score > 0.7 and entity.category in  ['Person', 'Organization', 'PhoneNumber', 'Address', 'Location', 'PhoneNumber', 'BankAccountNumber']:
            # print("Entity: {}".format(entity.text))
            pii_words.append(entity.text)
            # print("\tCategory: {}".format(entity.category))
            # print("\tConfidence Score: {}".format(entity.confidence_score))
            # print("\tOffset: {}".format(entity.offset))
            # print("\tLength: {}".format(entity.length))


pii_segments = map_pii_to_timestamps(pii_words, transcript['chunks'])
# pii_segments = map_pii_to_timestamps_with_words(pii_words, transcript['chunks'])
# print(pii_segments)

# Define the folder path
Annotations_folder_path = r"D:\Coding\PII Evaluation\Annotations output"

# Iterate over all files in the directory
for filename in os.listdir(Annotations_folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(Annotations_folder_path, filename)
        ground_truth=[]
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

                # print(f"--- Processing File: {filename} ---")
                
                # Extract and convert segments to seconds
                if "data" in data and "segments" in data["data"]:
                    segments = data["data"]["segments"]
                    # print("Segments (in seconds):")
                    for segment in segments:
                        start_sec = segment["start"] / 1000
                        end_sec = segment["end"] / 1000
                        ground_truth.append((start_sec, end_sec))
                        # print(f"  Start: {start_sec}s, End: {end_sec}s")

                # Fetch the file map for the WAV file
                if "file_map" in data:
                    wav_file_name = data["file_map"].get(data["files"]["audio"])
                    # print(f"Mapped WAV file name: {wav_file_name}")

                # print("\n")

        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filename}. Skipping.")
        except KeyError:
            print(f"Missing expected keys in {filename}. Skipping.")

# Annotations file path
annotations_file_path=r"D:\Coding\PII Evaluation\Annotations output\DS-19768.DP-0bbad67112dd4f3d8ae0a2b96d14184a.TS-2025-08-08T05-58-10.671Z.json"

# Function to get ground truth from JSON
def get_ground_truth_from_json(annotations_file_path):
    """
    Reads a single JSON file and extracts the ground truth segments in seconds.
    
    Args:
        annotations_file_path (str): The full path to the JSON annotation file.

    Returns:
        list: A list of (start_sec, end_sec) tuples, or an empty list if
              the file is invalid or required data is missing.
    """
    ground_truth = []
    
    try:
        with open(annotations_file_path, 'r') as f:
            data = json.load(f)
            
            # Extract and convert segments to seconds
            if "data" in data and "segments" in data["data"]:
                for segment in data["data"]["segments"]:
                    start_sec = segment["start"] / 1000
                    end_sec = segment["end"] / 1000
                    ground_truth.append((start_sec, end_sec))
            
    except FileNotFoundError:
        print(f"Error: The file at {annotations_file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {annotations_file_path}. Skipping.")
    except KeyError:
        print(f"Missing expected keys in {annotations_file_path}. Skipping.")

    return ground_truth



# Get the ground_truth list
ground_truth = get_ground_truth_from_json(annotations_file_path)

# print(f"Ground truth segments for the file: {ground_truth}")


predictions_ranges = sorted(pii_segments, key=lambda x: x)  # get the timestamps in a list

# print(predictions_ranges)


def calculate_overlap(range1, range2):
    """
    Calculate the overlap duration between two timestamp ranges.

    Parameters:
        range1 (tuple): (start1, end1) in seconds
        range2 (tuple): (start2, end2) in seconds
    
    Returns:
        float: Overlap duration in seconds. 0 if no overlap.
    """
    start1, end1 = range1
    start2, end2 = range2

    # Find the latest start time and earliest end time
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)

    # If the intervals overlap, overlap_start < overlap_end
    if overlap_start < overlap_end:
        return overlap_end - overlap_start
    else:
        return 0


def evaluate_ranges_any_overlap(ground_truth, predictions):
    tp, fp, fn, tn = 0, 0, 0, 0
    matched_gt = set()
    matched_pred = set()
    
    for pred_idx, pred_range in enumerate(predictions):
        found_overlap = False
        for gt_idx, gt_range in enumerate(ground_truth):
            if calculate_overlap(pred_range, gt_range) > 0:
                if gt_idx not in matched_gt and pred_idx not in matched_pred:
                    tp += 1
                    matched_gt.add(gt_idx)
                    matched_pred.add(pred_idx)
                    found_overlap = True
                    break
        if not found_overlap:
            fp += 1

    fn = len(ground_truth) - len(matched_gt)

    # Calculate TN: count of prediction/ground_truth pairs that do not overlap and are not already matched
    total_pairs = len(ground_truth) * len(predictions)
    overlap_pairs = 0
    for pred_idx, pred_range in enumerate(predictions):
        for gt_idx, gt_range in enumerate(ground_truth):
            if calculate_overlap(pred_range, gt_range) > 0:
                overlap_pairs += 1
    tn = total_pairs - overlap_pairs

    return tp, fp, fn, tn

# Get evaluation metrics
tp, fp, fn, tn = evaluate_ranges_any_overlap(ground_truth, predictions_ranges)

# Calculate standard metrics
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn)> 0 else 0

f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
f2_score = 5 * (precision * recall) / (4 * precision + recall) if (4 * precision + recall) > 0 else 0

print(f"True Positives: {tp}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Negatives: {tn}")
print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1 Score: {f1_score:.3f}")
print(f"F2 Score: {f2_score:.3f}")





