import tkinter as tk
from tkinter import filedialog, messagebox
import math
from collections import defaultdict
import re
import numpy as np
from summarizer_utils import (
    compute_tfidf_vectors,
    compute_cosine_similarity,
    get_graph,
    page_rank,
    get_sentences
)

from file_selector import (get_file, compare_summaries,log_summary_to_excel)
from metrics import (compute_precision, compute_recall)

file_name = ""

def select_file():
    global file_name

    # Clear old data display on textview
    text_output.delete(1.0, tk.END)
    text_old_output.delete(1.0, tk.END)

    try:
        threshold = float(entry_threshold.get())
        if not (0 <= threshold <= 1):
            raise ValueError
    except:
        threshold = 0.1

    try:
        _num_sentence = int(text_num_sentence.get("1.0", tk.END).strip())
    except ValueError:
        messagebox.showerror("Lỗi", "Giá trị số câu sau rút gọn không hợp lệ.")
        return

    file_path, file_name = get_file()
    sentences = get_sentences(file_path)

    count_sentence = len(sentences)
    if count_sentence == 0:
        messagebox.showinfo("Thông báo", "File không có câu nào để tóm tắt.")
        return

    if _num_sentence > count_sentence:
        messagebox.showwarning("Cảnh báo",
                               f"Số câu rút gọn ({_num_sentence}) lớn hơn số câu trong văn bản ({count_sentence}). Tự động giảm xuống {count_sentence}.")
        _num_sentence = count_sentence

    old_output_file_path = file_path.replace("input", "output")
    old_output_sentences = get_sentences(old_output_file_path)
    num_old_output_sentences = len(old_output_sentences)
    if num_old_output_sentences == 0:
        messagebox.showinfo("Thông báo", "Không tìm thấy file out của giáo viên.")
        return

    tfidf_vectors, _ = compute_tfidf_vectors(sentences)
    cosine_sim_matrix = compute_cosine_similarity(tfidf_vectors)
    graph = get_graph(sentences, cosine_sim_matrix, threshold=threshold)
    pagerank_scores = page_rank(graph, 0.85)

    ranked_sentences = sorted(((pagerank_scores[i], i) for i in range(count_sentence)), reverse=True)
    top_sentence_indices = [i for _, i in ranked_sentences[:_num_sentence]]
    top_sentence_indices.sort()

    summary_document = ' '.join([sentences[i] for i in top_sentence_indices])
    old_output_text = ' '.join(old_output_sentences)

    # Hiển thị kết quả tóm tắt và chuẩn bất kể match có hay không
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, summary_document)

    text_old_output.delete(1.0, tk.END)
    text_old_output.insert(tk.END, old_output_text)

    # So sánh các câu giống nhau (nếu có)
    match_count, matched_text = compare_summaries(summary_document, old_output_sentences)

    label_match_count.config(text=f"Số câu khớp: {match_count}/{_num_sentence}")

    precision = compute_precision(match_count, _num_sentence)
    label_precision.config(text=f"Precision: {precision:.5f}")

    recall = compute_recall(match_count, num_old_output_sentences)
    label_recall.config(text=f"recall: {recall:.5f}")

    log_summary_to_excel(
        file_name=file_name,
        num_summary_sentences=_num_sentence,
        num_reference_sentences=num_old_output_sentences,
        match_count=match_count,
        precision=precision,
        recall=recall
    )


    text_matched_sentences.config(state='normal')
    text_matched_sentences.delete(1.0, tk.END)
    if match_count > 0:
        text_matched_sentences.insert(tk.END, matched_text)
    else:
        text_matched_sentences.insert(tk.END, "(Không có câu nào khớp)")
    text_matched_sentences.config(state='disabled')


# UI setup
root = tk.Tk()
root.title("XML Text Summarizer")
root.state('zoomed')  # Windows

frame_top = tk.Frame(root)
frame_top.pack(pady=20)

label_num = tk.Label(frame_top, text="Số câu sau rút gọn", font=("Arial", 12))
label_num.pack(side=tk.LEFT)

text_num_sentence = tk.Text(frame_top, width=5, height=2, font=("Arial", 10))
text_num_sentence.insert("1.0", "10")
text_num_sentence.pack(side=tk.LEFT, padx=10)

label_threshold = tk.Label(frame_top, text="Ngưỡng threshold (0-1):", font=("Arial", 12))
label_threshold.pack(side=tk.LEFT, padx=(20, 0))

entry_threshold = tk.Entry(frame_top, width=6, font=("Arial", 12))
entry_threshold.insert(0, "0.1")
entry_threshold.pack(side=tk.LEFT, padx=10)

btn_select = tk.Button(frame_top, text="Chọn file XML", command=select_file, font=("Arial", 12), padx=10, pady=5)
btn_select.pack(side=tk.LEFT)

# Frame hiển thị kết quả so khớp
# Frame hiển thị kết quả so khớp
frame_match = tk.Frame(root)
frame_match.pack(fill="x", padx=10, pady=5)

# Frame nhỏ để chứa 2 label trên cùng 1 hàng
frame_labels = tk.Frame(frame_match)
frame_labels.pack(fill="x")

label_match_count = tk.Label(frame_labels, text="Số câu khớp: 0", font=("Arial", 11, "bold"))
label_match_count.pack(side=tk.LEFT, padx=(0, 20))

label_precision = tk.Label(frame_labels, text="Precision: 0.00", font=("Arial", 11, "bold"))
label_precision.pack(side=tk.LEFT)

label_recall = tk.Label(frame_labels, text="Recall: 0.00", font=("Arial", 11, "bold"))
label_recall.pack(side=tk.LEFT, padx=(20, 0))

# Text nằm dòng dưới 2 label
text_matched_sentences = tk.Text(frame_match, height=5, font=("Arial", 10), bg="#eef5f9", state='disabled', wrap="word")
text_matched_sentences.pack(fill="x", pady=(5,0))

# Frame chứa hai ô Text
frame_bottom = tk.Frame(root)
frame_bottom.pack(expand=True, fill="both", padx=10, pady=10)

# Text chính (tóm tắt)
text_output = tk.Text(frame_bottom, wrap="word", font=("Arial", 10))
text_output.pack(side=tk.LEFT, expand=True, fill="both")

# Text mới bên cạnh
text_old_output = tk.Text(frame_bottom, wrap="word", font=("Arial", 10), bg="#f5f5f5")
text_old_output.pack(side=tk.LEFT, expand=True, fill="both")

# Scrollbar áp dụng cho text_output
scrollbar = tk.Scrollbar(frame_bottom, command=text_output.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_output.config(yscrollcommand=scrollbar.set)

root.mainloop()
