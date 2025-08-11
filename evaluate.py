import os
import json
from packages.transcripts import transcribe_with_timestamps
from packages.PII_detection import detect_pii_entities
from packages.mapTimeStamps import map_pii_to_timestamps

# Paths
input_audio_path = r"D:\Coding\PII Evaluation\main server dataset\phase 3\4547022.wav"
annotations_folder_path = r"D:\Coding\PII Evaluation\Annotations output"
annotations_file_path = r"D:\Coding\PII Evaluation\Annotations output\DS-19768.DP-0bbad67112dd4f3d8ae0a2b96d14184a.TS-2025-08-08T05-58-10.671Z.json"

def get_ground_truth_from_json(file_path):
    """Extract ground truth segments (in seconds) from a JSON annotation file."""
    ground_truth = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if "data" in data and "segments" in data["data"]:
                for segment in data["data"]["segments"]:
                    start_sec = segment["start"] / 1000
                    end_sec = segment["end"] / 1000
                    ground_truth.append((start_sec, end_sec))
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        print(f"Error processing {file_path}. Skipping.")
    return ground_truth

def calculate_overlap(range1, range2):
    """Calculate overlap duration between two timestamp ranges."""
    start1, end1 = range1
    start2, end2 = range2
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    return max(0, overlap_end - overlap_start)

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
    total_pairs = len(ground_truth) * len(predictions)
    overlap_pairs = sum(
        1 for pred_range in predictions for gt_range in ground_truth
        if calculate_overlap(pred_range, gt_range) > 0
    )
    tn = total_pairs - overlap_pairs
    return tp, fp, fn, tn

def main():
    # Transcribe audio and detect PII
    transcript = transcribe_with_timestamps(input_audio_path)
    asr_text = [transcript['text']]
    pii_result = detect_pii_entities(asr_text)
    pii_words = [
        entity.text
        for doc in pii_result
        for entity in doc.entities
        if entity.confidence_score > 0.7 and entity.category in [
            'Person', 'Organization', 'PhoneNumber', 'Address', 'Location', 'BankAccountNumber'
        ]
    ]
    pii_segments = map_pii_to_timestamps(pii_words, transcript['chunks'])
    predictions_ranges = sorted(pii_segments, key=lambda x: x)

    # Get ground truth
    ground_truth = get_ground_truth_from_json(annotations_file_path)

    # Evaluate
    tp, fp, fn, tn = evaluate_ranges_any_overlap(ground_truth, predictions_ranges)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) > 0 else 0
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

if __name__ == "__main__":
    main()
