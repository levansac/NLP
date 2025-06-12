# metrics.py

def compute_precision(match_count, predicted_count):
    if predicted_count == 0:
        return 0.0
    return match_count / predicted_count

def compute_recall(match_count: int, total_relevant: int) -> float:
    if total_relevant == 0:
        return 0.0
    return match_count / total_relevant

def compute_f1(precision, recall):
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)
