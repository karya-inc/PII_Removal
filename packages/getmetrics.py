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

def evaluate_and_metrics(ground_truth, predictions):
    """
    Evaluate TP, FP, FN, TN and calculate accuracy, precision, recall, F1, F2.
    Returns a dictionary of all metrics.
    """
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
    overlap_pairs = 0
    for pred_range in predictions:
        for gt_range in ground_truth:
            if calculate_overlap(pred_range, gt_range) > 0:
                overlap_pairs += 1
    tn = total_pairs - overlap_pairs

    metrics = calculate_metrics(tp, fp, fn, tn)
    metrics.update({'True Positive': tp, 'False Positive': fp, 'False Negative': fn, 'True Negative': tn})
    return metrics

def calculate_metrics(tp, fp, fn, tn):
    """
    Calculate accuracy, precision, recall, F1, F2 scores.
    """
    precision = round(tp / (tp + fp), 2) if (tp + fp) > 0 else 0
    recall = round(tp / (tp + fn), 2) if (tp + fn) > 0 else 0
    accuracy = round((tp + tn) / (tp + fp + fn + tn), 2) if (tp + fp + fn + tn) > 0 else 0
    f1_score = round(2 * (precision * recall) / (precision + recall), 2) if (precision + recall) > 0 else 0
    f2_score = round(5 * (precision * recall) / (4 * precision + recall), 2) if (4 * precision + recall) > 0 else 0
    return {
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1_score,
        'F2 Score': f2_score
    }

# Example usage:
# metrics = evaluate_and_metrics(ground_truth, sorted_ranges)
# print(metrics)
