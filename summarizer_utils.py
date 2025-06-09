import math
from collections import defaultdict
from tkinter import messagebox

import numpy as np
import re
from collections import Counter

def get_sentences(file_path):
    try:
        sentences = []
        pattern = re.compile(r'<s[^>]*>(.*?)</s>')
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                matches = pattern.findall(line)
                for match in matches:
                    sentence = match.strip()
                    if sentence:
                        sentences.append(sentence)
        return sentences
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi đọc file:\n{e}")

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())


def compute_tf(sent_tokens):
    tf_list = []
    for tokens in sent_tokens:
        term_count = Counter(tokens)
        total_terms = len(tokens)
        tf = {term: count / total_terms for term, count in term_count.items()}
        tf_list.append(tf)
    return tf_list

def compute_idf(sent_tokens):
    N = len(sent_tokens)
    df = defaultdict(int)
    for tokens in sent_tokens:
        for term in set(tokens):
            df[term] += 1
    idf = {term: math.log(N / (1 + freq)) for term, freq in df.items()}
    return idf


def compute_tfidf_vectors(sentences):
    sent_tokens = [tokenize(sentence) for sentence in sentences] #Chuyển mỗi câu thành danh sách các từ (tokens).
    tf_list = compute_tf(sent_tokens) #Tính tần suất xuất hiện của mỗi từ trong từng câu (sau khi token hóa).
    idf = compute_idf(sent_tokens) #Tính độ hiếm của từ trong toàn bộ văn bản. Nếu từ xuất hiện trong nhiều câu, IDF của nó sẽ thấp (ít quan trọng).
    vocabulary = sorted(idf.keys())

    tfidf_vectors = []
    for tf in tf_list:
        vec = []
        for term in vocabulary:
            tfidf = tf.get(term, 0.0) * idf.get(term, 0.0)
            vec.append(tfidf)
        tfidf_vectors.append(vec)

    return tfidf_vectors, vocabulary


def cosine_sim(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def compute_cosine_similarity(tfidf_vectors):
    tfidf_array = np.array(tfidf_vectors)
    norms = np.linalg.norm(tfidf_array, axis=1)
    sim_matrix = np.zeros((len(tfidf_array), len(tfidf_array)))

    for i in range(len(tfidf_array)):
        for j in range(i, len(tfidf_array)):
            if norms[i] == 0 or norms[j] == 0:
                sim = 0.0
            else:
                sim = np.dot(tfidf_array[i], tfidf_array[j]) / (norms[i] * norms[j])
            sim_matrix[i][j] = sim
            sim_matrix[j][i] = sim  # symmetry
    return sim_matrix

def get_graph(sentences, cosine_sim_matrix, threshold=0.1):
    count = len(sentences)
    graph = {}
    for i in range(count):
        graph[i] = {}
        for j in range(count):
            if i != j:
                sim = cosine_sim_matrix[i][j]
                if sim >= threshold:  # Chỉ thêm cạnh nếu similarity lớn hơn hoặc bằng threshold
                    graph[i][j] = sim
    return graph


def page_rank(graph, d=0.85, max_iterations=30, tol=1.0e-3):
    nodes = list(graph.keys())
    N = len(nodes)
    pr = {node: 1.0 / N for node in nodes}
    sink_nodes = [node for node in nodes if len(graph[node]) == 0]

    for _ in range(max_iterations):
        new_pr = {}
        for node in nodes:
            rank = (1 - d) / N
            for other_node in nodes:
                if node in graph[other_node]:
                    weight = graph[other_node][node]
                    total_weight = sum(graph[other_node].values())
                    rank += d * pr[other_node] * (weight / total_weight if total_weight > 0 else 0)
                elif other_node in sink_nodes:
                    rank += d * pr[other_node] / N
            new_pr[node] = rank

        diff = sum(abs(new_pr[n] - pr[n]) for n in nodes)
        pr = new_pr
        if diff < tol:
            break
    return pr
