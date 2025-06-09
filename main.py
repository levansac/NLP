import string
import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
# Import các hàm bạn có sẵn từ các file module của bạn
from summarizer_utils import (
    compute_tfidf_vectors,
    compute_cosine_similarity,
    get_graph,
    page_rank,
    get_sentences
)

from file_selector import get_file, compare_summaries, log_summary_to_excel
from metrics import compute_precision, compute_recall

file_name = ""

def select_file():
    global file_name

    # Xóa dữ liệu cũ trong Text
    text_output.delete(1.0, tk.END)
    text_old_output.delete(1.0, tk.END)

    try:
        threshold = float(entry_threshold.get())
        if not (0 <= threshold <= 1):
            raise ValueError
    except:
        threshold = 0.1

    try:
        _num_sentence = int(entry_num_sentence.get().strip())
    except ValueError:
        messagebox.showerror("Lỗi", "Giá trị số câu sau rút gọn không hợp lệ.")
        return

    file_path, file_name = get_file()
    if not file_path:
        return  # Người dùng hủy chọn file

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

    # So sánh các câu giống nhau
    match_count, matched_text = compare_summaries(summary_document, old_output_sentences)

    label_match_count.config(text=f"Số câu khớp: {match_count}/{_num_sentence}")

    precision = compute_precision(match_count, _num_sentence)
    label_precision.config(text=f"Precision: {precision:.5f}")

    recall = compute_recall(match_count, num_old_output_sentences)
    label_recall.config(text=f"Recall: {recall:.5f}")

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

    # Hiển thị kết quả tóm tắt và chuẩn
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, summary_document)
    text_old_output.delete(1.0, tk.END)
    text_old_output.insert(tk.END, old_output_text)

root = tk.Tk()
root.title("XML Text Summarizer")
root.state('zoomed')  # Windows

# Style và theme
style = ttk.Style(root)
style.theme_use('clam')

# ===== Top Frame: nhập tham số =====
frame_top = ttk.Frame(root, padding=15)
frame_top.grid(row=0, column=0, sticky="ew")

# Số câu sau rút gọn (dùng Entry thay Text cho gọn)
label_num = ttk.Label(frame_top, text="Số câu sau rút gọn:", font=("Segoe UI", 11))
label_num.grid(row=0, column=0, sticky="w")

entry_num_sentence = ttk.Entry(frame_top, width=5, font=("Segoe UI", 11))
entry_num_sentence.insert(0, "10")
entry_num_sentence.grid(row=0, column=1, padx=(5, 25))

# Ngưỡng threshold
label_threshold = ttk.Label(frame_top, text="Ngưỡng threshold (0-1):", font=("Segoe UI", 11))
label_threshold.grid(row=0, column=2, sticky="w")

entry_threshold = ttk.Entry(frame_top, width=6, font=("Segoe UI", 11))
entry_threshold.insert(0, "0.1")
entry_threshold.grid(row=0, column=3, padx=(5, 25))

# Button chọn file
btn_select = ttk.Button(frame_top, text="Chọn file XML", command=select_file)
btn_select.grid(row=0, column=4)

# Cho frame_top co giãn ngang
frame_top.columnconfigure(4, weight=1)

# ===== Frame match info =====
frame_match = ttk.LabelFrame(root, text="Kết quả so khớp", padding=10)
frame_match.grid(row=1, column=0, sticky="ew", padx=15, pady=(5,10))

label_match_count = ttk.Label(frame_match, text="Số câu khớp: 0", font=("Segoe UI", 10, "bold"))
label_match_count.grid(row=0, column=0, sticky="w", padx=(0, 20))

label_precision = ttk.Label(frame_match, text="Precision: 0.00", font=("Segoe UI", 10, "bold"))
label_precision.grid(row=0, column=1, sticky="w", padx=(0, 20))

label_recall = ttk.Label(frame_match, text="Recall: 0.00", font=("Segoe UI", 10, "bold"))
label_recall.grid(row=0, column=2, sticky="w")

# Text matched sentences (disabled)
text_matched_sentences = tk.Text(frame_match, height=5, font=("Segoe UI", 10), bg="#eef5f9", state='disabled', wrap="word")
text_matched_sentences.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))

frame_match.columnconfigure(2, weight=1)

# ===== Frame main bottom: 2 Text (summary vs old output) =====
frame_bottom = ttk.Frame(root, padding=10)
frame_bottom.grid(row=2, column=0, sticky="nsew")

root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)
frame_bottom.columnconfigure(0, weight=1)
frame_bottom.columnconfigure(1, weight=1)
frame_bottom.rowconfigure(0, weight=1)

# Text tóm tắt
frame_summary = ttk.LabelFrame(frame_bottom, text="Tóm tắt", padding=5)
frame_summary.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
frame_summary.rowconfigure(0, weight=1)
frame_summary.columnconfigure(0, weight=1)

text_output = tk.Text(frame_summary, wrap="word", font=("Segoe UI", 11))
text_output.grid(row=0, column=0, sticky="nsew")

scrollbar_out = ttk.Scrollbar(frame_summary, command=text_output.yview)
scrollbar_out.grid(row=0, column=1, sticky='ns')
text_output.config(yscrollcommand=scrollbar_out.set)

# Text chuẩn (old output)
frame_old_output = ttk.LabelFrame(frame_bottom, text="Chuẩn", padding=5)
frame_old_output.grid(row=0, column=1, sticky="nsew")
frame_old_output.rowconfigure(0, weight=1)
frame_old_output.columnconfigure(0, weight=1)

text_old_output = tk.Text(frame_old_output, wrap="word", font=("Segoe UI", 11), bg="#f5f5f5")
text_old_output.grid(row=0, column=0, sticky="nsew")

scrollbar_old = ttk.Scrollbar(frame_old_output, command=text_old_output.yview)
scrollbar_old.grid(row=0, column=1, sticky='ns')
text_old_output.config(yscrollcommand=scrollbar_old.set)

root.mainloop()
