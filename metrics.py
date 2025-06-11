# metrics.py

def compute_precision(match_count, predicted_count):
    """
    Tính precision = số câu khớp / số câu dự đoán (output)

    Args:
        match_count (int): số câu khớp giữa tóm tắt và kết quả chuẩn
        predicted_count (int): số câu tóm tắt được sinh ra (output)

    Returns:
        float: precision, trong khoảng [0,1]. Nếu predicted_count = 0 thì trả về 0 để tránh chia 0.
    """
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
