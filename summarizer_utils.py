import math
from collections import defaultdict
import numpy as np
import re
from collections import Counter

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def compute_tf(sent_tokens):
    tf_list = []

    for tokens in sent_tokens:
        term_count = Counter(tokens)                # Đếm số lần xuất hiện của mỗi từ
        total_terms = len(tokens)                   # Tổng số từ trong câu
        tf = {term: count / total_terms for term, count in term_count.items()}  # Tính tần suất
        tf_list.append(tf)

    return tf_list

def compute_idf(sent_tokens):
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
    # 1. Token hóa các câu (tách từ)
    sent_tokens = [tokenize(sentence) for sentence in sentences]
    # 2. Tính TF (Term Frequency) cho từng câu
    tf_list = compute_tf(sent_tokens)
    # 3. Tính IDF (Inverse Document Frequency) cho toàn bộ từ vựng
    # (Nếu từ xuất hiện trong nhiều câu, IDF của nó sẽ thấp (ít quan trọng).)
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
    # Chuyển danh sách TF-IDF thành mảng numpy để tính toán hiệu quả hơn
    tfidf_array = np.array(tfidf_vectors)

    # Tính chuẩn (norm) của từng vector, Kết quả: norms là một mảng 1 chiều có n phần tử,
    # mỗi phần tử là độ dài của một vector TF-IDF.
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

def page_rank(graph, d=0.85, max_loop=50, tol=1.0e-4):
    nodes = list(graph.keys())
    num_node = len(nodes)
    pagerank_score = {node: 1.0 for node in nodes}

    for _ in range(max_loop):# (1) Lặp qua từng vòng cập nhật
        current_pr = {}
        for node in nodes:# (2) Lặp qua từng node để tính lại điểm
            rank = (1 - d) / num_node
            for other_node in nodes:# (3) Lặp qua các node khác để xem ai trỏ tới node đang xét
                if node in graph[other_node]:
                    weight = graph[other_node][node]
                    total_weight = sum(graph[other_node].values())
                    if total_weight > 0: #check is not empty node
                        rank += d * pagerank_score[other_node] * (weight / total_weight)
            current_pr[node] = rank
        pagerank_score = current_pr
        diff = sum(abs(current_pr[n] - pagerank_score[n]) for n in nodes)
        if diff < tol:
            break

    return pagerank_score
