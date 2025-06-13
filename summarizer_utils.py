import math
from collections import defaultdict
import numpy as np
import re
from collections import Counter

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def compute_tf(sent_tokens):
    """
    Tính TF (Term Frequency) – tần suất xuất hiện của từ trong từng câu.

    Parameters:
        sent_tokens (List[List[str]]): Danh sách các câu, mỗi câu là danh sách từ (tokens).

    Returns:
        List[Dict[str, float]]: Danh sách các từ điển TF, mỗi từ điển tương ứng với một câu.
    """
    tf_list = []

    for tokens in sent_tokens:
        term_count = Counter(tokens)                # Đếm số lần xuất hiện của mỗi từ
        total_terms = len(tokens)                   # Tổng số từ trong câu
        tf = {term: count / total_terms for term, count in term_count.items()}  # Tính tần suất
        tf_list.append(tf)

    return tf_list


def compute_idf(sent_tokens):
    """
    Tính độ đo IDF (Inverse Document Frequency) cho từng từ trong danh sách câu đã được token hóa.

    Parameters:
        sent_tokens (List[List[str]]): Danh sách các câu, mỗi câu là danh sách các từ (tokens).

    Returns:
        dict: Từ điển chứa IDF của từng từ.
    """

    N = len(sent_tokens)  # Tổng số câu trong văn bản
    df = defaultdict(int)  # Document Frequency: số câu chứa từ

    # Duyệt qua từng câu
    for tokens in sent_tokens:
        unique_terms = set(tokens)  # Tránh đếm trùng từ trong cùng một câu
        for term in unique_terms:
            df[term] += 1

    # Tính IDF: thêm 1 vào mẫu để tránh chia cho 0
    idf = {term: math.log(N / (1 + freq)) for term, freq in df.items()}

    return idf


def compute_tfidf_vectors(sentences):
    """
    Chuyển danh sách câu văn thành các vector TF-IDF.

    Parameters:
        sentences (List[str]): Danh sách các câu gốc.

    Returns:
        List[List[float]]: Danh sách vector TF-IDF ứng với từng câu.
        List[str]: Danh sách từ vựng được dùng làm trục vector (sorted).
    """
    # 1. Token hóa các câu (tách từ)
    sent_tokens = [tokenize(sentence) for sentence in sentences]
    # 2. Tính TF (Term Frequency) cho từng câu
    tf_list = compute_tf(sent_tokens)
    # 3. Tính IDF (Inverse Document Frequency) cho toàn bộ từ vựng (Nếu từ xuất hiện trong nhiều câu, IDF của nó sẽ thấp (ít quan trọng).)
    idf = compute_idf(sent_tokens)
    # 4. Tạo từ vựng thống nhất, sắp xếp để đảm bảo thứ tự vector
    vocabulary = sorted(idf.keys())
    # 5. Tính vector TF-IDF cho từng câu
    tfidf_vectors = []
    for tf in tf_list:
        vec = []
        for term in vocabulary:
            tfidf = tf.get(term, 0.0) * idf.get(term, 0.0)
            vec.append(tfidf)
        tfidf_vectors.append(vec)

    return tfidf_vectors, vocabulary

def compute_cosine_similarity(tfidf_vectors):
    """
    Tính ma trận độ tương đồng Cosine giữa các vector TF-IDF đại diện cho các câu.

    Parameters:
        tfidf_vectors (List[List[float]]): Danh sách các vector TF-IDF.

    Returns:
        np.ndarray: Ma trận tương đồng cosine (n x n), với mỗi phần tử [i][j] là độ tương đồng giữa câu i và câu j.
    """

    # Chuyển danh sách TF-IDF thành mảng numpy để tính toán hiệu quả hơn
    tfidf_array = np.array(tfidf_vectors)

    # Tính chuẩn (norm) của từng vector, Kết quả: norms là một mảng 1 chiều có n phần tử, mỗi phần tử là độ dài của một vector TF-IDF.
    norms = np.linalg.norm(tfidf_array, axis=1) #axis=1: thực hiện chuẩn hóa theo từng dòng, tức là chuẩn hóa từng vector TF-IDF.

    # Khởi tạo ma trận tương đồng (n x n) với 0
    sim_matrix = np.zeros((len(tfidf_array), len(tfidf_array)))

    # Tính cosine similarity giữa từng cặp câu
    for i in range(len(tfidf_array)):
        for j in range(i, len(tfidf_array)):
            if norms[i] == 0 or norms[j] == 0:
                sim = 0.0  # Nếu vector rỗng, tương đồng bằng 0
            else:
                # tfidf_array[i] và tfidf_array[j]: là hai vector TF-IDF tương ứng với câu thứ i và j.
                # np.dot(tfidf_array[i], tfidf_array[j]): tính tích vô hướng (dot product) giữa hai vector.
                # norms[i] * norms[j]: là tích độ dài (norm) của hai vector.
                sim = np.dot(tfidf_array[i], tfidf_array[j]) / (norms[i] * norms[j])
            sim_matrix[i][j] = sim
            sim_matrix[j][i] = sim  # Vì ma trận là đối xứng

    return sim_matrix

def get_graph(sentences, cosine_sim_matrix, threshold=0.1):
    """
    Xây đồ thị có trọng số từ ma trận độ tương đồng cosine.

    Mỗi câu là một đỉnh trong đồ thị. Một cạnh được tạo giữa hai đỉnh nếu
    độ tương đồng giữa hai câu lớn hơn hoặc bằng ngưỡng (threshold).

    Parameters:
        sentences (List[str]): Danh sách các câu.
        cosine_sim_matrix (np.ndarray): Ma trận độ tương đồng cosine.
        threshold (float): Ngưỡng để thêm cạnh giữa các đỉnh.

    Returns:
        Dict[int, Dict[int, float]]: Đồ thị dưới dạng dictionary với trọng số cạnh.
    """
    count = len(sentences)
    graph = {}

    for i in range(count):
        graph[i] = {}
        for j in range(count):
            if i != j:
                sim = cosine_sim_matrix[i][j]
                if sim >= threshold:
                    graph[i][j] = sim  # Thêm cạnh từ i đến j với trọng số sim

    return graph

def page_rank(graph, d=0.85, max_iterations=50, tol=1.0e-5):
    """
    Áp dụng thuật toán PageRank để xếp hạng độ quan trọng của các đỉnh trong đồ thị.

    Parameters:
        graph (dict): Đồ thị có trọng số, dạng {node: {neighbor: weight}}.
        d (float): Hệ số suy giảm (damping factor), mặc định là 0.85.
        max_iterations (int): Số vòng lặp tối đa.
        tol (float): Ngưỡng hội tụ (sai số nhỏ hơn tol thì dừng).

    Returns:
        dict: Kết quả PageRank, dạng {node: score}, sắp xếp giảm dần không.
    """
    nodes = list(graph.keys())
    N = len(nodes)

    # Khởi tạo giá trị PageRank đều nhau
    pr = {node: 1.0 / N for node in nodes}

    # Danh sách các đỉnh không có liên kết ra (sink nodes)
    sink_nodes = [node for node in nodes if len(graph[node]) == 0]

    # Bắt đầu lặp tính PageRank
    for _ in range(max_iterations):
        new_pr = {}

        for node in nodes:
            rank = (1 - d) / N  # Phần cơ bản

            for other_node in nodes:
                if node in graph[other_node]:
                    weight = graph[other_node][node]
                    total_weight = sum(graph[other_node].values())
                    if total_weight > 0:
                        rank += d * pr[other_node] * (weight / total_weight)
                elif other_node in sink_nodes:
                    # Sink node đóng góp đều cho tất cả các đỉnh
                    rank += d * pr[other_node] / N

            new_pr[node] = rank

        # Kiểm tra điều kiện hội tụ
        diff = sum(abs(new_pr[n] - pr[n]) for n in nodes)
        pr = new_pr

        if diff < tol:
            break

    return pr

