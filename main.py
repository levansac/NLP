# import string
# import tkinter as tk
# from tkinter import ttk, messagebox
# import os
# from datetime import datetime
# # Import các hàm bạn có sẵn từ các file module của bạn
# from summarizer_utils import (
#     compute_tfidf_vectors,
#     compute_cosine_similarity,
#     get_graph,
#     page_rank,
#     get_sentences
# )
#
# from file_selector import get_file, compare_summaries,compare_summaries_cosine, log_summary_to_excel
# from metrics import compute_precision, compute_recall
#
# file_name = ""
#
# def select_file():
#     global file_name
#
#     # Xóa dữ liệu cũ trong Text
#     text_output.delete(1.0, tk.END)
#     text_old_output.delete(1.0, tk.END)
#
#     try:
#         threshold = float(entry_threshold.get())
#         if not (0 <= threshold <= 1):
#             raise ValueError
#     except:
#         threshold = 0.1
#
#     try:
#         _num_sentence = int(entry_num_sentence.get().strip())
#     except ValueError:
#         messagebox.showerror("Lỗi", "Giá trị số câu sau rút gọn không hợp lệ.")
#         return
#
#     file_path, file_name = get_file()
#     if not file_path:
#         return  # Người dùng hủy chọn file
#
#     sentences = get_sentences(file_path)
#
#     count_sentence = len(sentences)
#     if count_sentence == 0:
#         messagebox.showinfo("Thông báo", "File không có câu nào để tóm tắt.")
#         return
#
#     if _num_sentence > count_sentence:
#         messagebox.showwarning("Cảnh báo",
#                                f"Số câu rút gọn ({_num_sentence}) lớn hơn số câu trong văn bản ({count_sentence}). Tự động giảm xuống {count_sentence}.")
#         _num_sentence = count_sentence
#
#     old_output_file_path = file_path.replace("input", "output")
#     old_output_sentences = get_sentences(old_output_file_path)
#     num_old_output_sentences = len(old_output_sentences)
#     if num_old_output_sentences == 0:
#         messagebox.showinfo("Thông báo", "Không tìm thấy file out của giáo viên.")
#         return
#
#     tfidf_vectors, _ = compute_tfidf_vectors(sentences)
#     cosine_sim_matrix = compute_cosine_similarity(tfidf_vectors)
#     graph = get_graph(sentences, cosine_sim_matrix, threshold=threshold)
#     pagerank_scores = page_rank(graph, 0.85)
#
#     ranked_sentences = sorted(((pagerank_scores[i], i) for i in range(count_sentence)), reverse=True)
#     top_sentence_indices = [i for _, i in ranked_sentences[:_num_sentence]]
#     top_sentence_indices.sort()
#
#     summary_document = ' '.join([sentences[i] for i in top_sentence_indices])
#     old_output_text = ' '.join(old_output_sentences)
#
#     # So sánh các câu giống nhau
#     # match_count, matched_text = compare_summaries(summary_document, old_output_sentences)
#     match_count, matched_text = compare_summaries_cosine(summary_document, old_output_sentences)
#
#     label_expected.config(text=f"Extracted: {num_old_output_sentences}")
#     label_extracted.config(text=f"Extracted: {_num_sentence}")
#     label_match_count.config(text=f"Correct: {match_count}")
#
#     precision = compute_precision(match_count, _num_sentence)
#     label_precision.config(text=f"Precision: {precision:.5f}")
#
#     recall = compute_recall(match_count, num_old_output_sentences)
#     label_recall.config(text=f"Recall: {recall:.5f}")
#
#     log_summary_to_excel(
#         file_name=file_name,
#         num_summary_sentences=_num_sentence,
#         num_reference_sentences=num_old_output_sentences,
#         match_count=match_count,
#         precision=precision,
#         recall=recall
#     )
#
#     text_matched_sentences.config(state='normal')
#     text_matched_sentences.delete(1.0, tk.END)
#     if match_count > 0:
#         text_matched_sentences.insert(tk.END, matched_text)
#     else:
#         text_matched_sentences.insert(tk.END, "(Không có câu nào khớp)")
#     text_matched_sentences.config(state='disabled')
#
#     # Hiển thị kết quả tóm tắt và chuẩn
#     text_output.delete(1.0, tk.END)
#     text_output.insert(tk.END, summary_document)
#     text_old_output.delete(1.0, tk.END)
#     text_old_output.insert(tk.END, old_output_text)
#
# root = tk.Tk()
# root.title("XML Text Summarizer")
# root.state('zoomed')  # Windows
#
# # Style và theme
# style = ttk.Style(root)
# style.theme_use('clam')
#
# # ===== Top Frame: nhập tham số =====
# frame_top = ttk.Frame(root, padding=15)
# frame_top.grid(row=0, column=0, sticky="ew")
#
# # Số câu sau rút gọn (dùng Entry thay Text cho gọn)
# label_num = ttk.Label(frame_top, text="Số câu sau rút gọn:", font=("Segoe UI", 11))
# label_num.grid(row=0, column=0, sticky="w")
#
# entry_num_sentence = ttk.Entry(frame_top, width=5, font=("Segoe UI", 11))
# entry_num_sentence.insert(0, "10")
# entry_num_sentence.grid(row=0, column=1, padx=(5, 25))
#
# # Ngưỡng threshold
# label_threshold = ttk.Label(frame_top, text="Ngưỡng threshold (0-1):", font=("Segoe UI", 11))
# label_threshold.grid(row=0, column=2, sticky="w")
#
# entry_threshold = ttk.Entry(frame_top, width=6, font=("Segoe UI", 11))
# entry_threshold.insert(0, "0.1")
# entry_threshold.grid(row=0, column=3, padx=(5, 25))
#
# # Button chọn file
# btn_select = ttk.Button(frame_top, text="Chọn file XML", command=select_file)
# btn_select.grid(row=0, column=4)
#
# # Cho frame_top co giãn ngang
# frame_top.columnconfigure(4, weight=1)
#
# # ===== Frame match info =====
# frame_match = ttk.LabelFrame(root, text="Kết quả so khớp", padding=10)
# frame_match.grid(row=1, column=0, sticky="ew", padx=15, pady=(5,10))
#
# # Label "Expected"
# label_filename = ttk.Label(frame_match, text="File Name:", font=("Segoe UI", 10, "bold"))
# label_filename.grid(row=0, column=0, sticky="w", padx=(0, 15))
#
# # Label "Expected"
# label_expected = ttk.Label(frame_match, text="Expected: 0", font=("Segoe UI", 10, "bold"))
# label_expected.grid(row=0, column=1, sticky="w", padx=(0, 20))
#
# # Label "Extracted"
# label_extracted = ttk.Label(frame_match, text="Extracted: 0", font=("Segoe UI", 10, "bold"))
# label_extracted.grid(row=0, column=2, sticky="w", padx=(0, 20))
#
# # Số câu khớp
# label_match_count = ttk.Label(frame_match, text="Correct: 0", font=("Segoe UI", 10, "bold"))
# label_match_count.grid(row=0, column=3, sticky="w", padx=(0, 20))
#
# # Precision và Recall
# label_precision = ttk.Label(frame_match, text="Precision: 0.00000", font=("Segoe UI", 10, "bold"))
# label_precision.grid(row=0, column=4, sticky="w", padx=(0, 20))
#
# label_recall = ttk.Label(frame_match, text="Recall: 0.00000", font=("Segoe UI", 10, "bold"))
# label_recall.grid(row=0, column=5, sticky="w")
#
# label_f1 = ttk.Label(frame_match, text="F1-score: 0.00000", font=("Segoe UI", 10, "bold"))
# label_f1.grid(row=0, column=6, sticky="w", padx=(0, 20))
#
# # Text matched sentences (disabled)
# text_matched_sentences = tk.Text(frame_match, height=5, font=("Segoe UI", 10), bg="#eef5f9", state='disabled', wrap="word")
# text_matched_sentences.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(10, 0))
#
# frame_match.columnconfigure(4, weight=1)
#
# # ===== Frame main bottom: 2 Text (summary vs old output) =====
# frame_bottom = ttk.Frame(root, padding=10)
# frame_bottom.grid(row=2, column=0, sticky="nsew")
#
# root.rowconfigure(2, weight=1)
# root.columnconfigure(0, weight=1)
# frame_bottom.columnconfigure(0, weight=1)
# frame_bottom.columnconfigure(1, weight=1)
# frame_bottom.rowconfigure(0, weight=1)
#
# # Text tóm tắt
# frame_summary = ttk.LabelFrame(frame_bottom, text="Summarizing data", padding=5)
# frame_summary.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
# frame_summary.rowconfigure(0, weight=1)
# frame_summary.columnconfigure(0, weight=1)
#
# text_output = tk.Text(frame_summary, wrap="word", font=("Segoe UI", 11))
# text_output.grid(row=0, column=0, sticky="nsew")
#
# scrollbar_out = ttk.Scrollbar(frame_summary, command=text_output.yview)
# scrollbar_out.grid(row=0, column=1, sticky='ns')
# text_output.config(yscrollcommand=scrollbar_out.set)
#
# # Text chuẩn (old output)
# frame_old_output = ttk.LabelFrame(frame_bottom, text="Standard data", padding=5)
# frame_old_output.grid(row=0, column=1, sticky="nsew")
# frame_old_output.rowconfigure(0, weight=1)
# frame_old_output.columnconfigure(0, weight=1)
#
# text_old_output = tk.Text(frame_old_output, wrap="word", font=("Segoe UI", 11), bg="#f5f5f5")
# text_old_output.grid(row=0, column=0, sticky="nsew")
#
# scrollbar_old = ttk.Scrollbar(frame_old_output, command=text_old_output.yview)
# scrollbar_old.grid(row=0, column=1, sticky='ns')
# text_old_output.config(yscrollcommand=scrollbar_old.set)
#
# root.mainloop()
import string
import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime

from summarizer_utils import (
    compute_tfidf_vectors,
    compute_cosine_similarity,
    get_graph,
    page_rank,
    get_sentences
)

from file_selector import get_file, compare_summaries_cosine, log_summary_to_excel
from metrics import compute_precision, compute_recall, compute_f1

file_name = ""

def create_info_pair(parent, label_text, default_text, col):
    frame = ttk.Frame(parent)
    frame.grid(row=0, column=col, padx=(5, 15), sticky="w")
    ttk.Label(frame, text=label_text, font=("Segoe UI", 10)).pack(side="left")
    lbl = ttk.Label(frame, text=default_text, font=("Segoe UI", 10, "bold"))
    lbl.pack(side="left")
    return lbl

def select_file():
    global file_name

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
        return

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

    summary_document = '\n'.join([sentences[i] for i in top_sentence_indices])
    old_output_text = '\n'.join(old_output_sentences)

    match_count, matched_text = compare_summaries_cosine(summary_document, old_output_sentences)

    label_expected.config(text=f"{num_old_output_sentences}")
    label_extracted.config(text=f"{_num_sentence}")
    label_match_count.config(text=f"{match_count}")

    precision = compute_precision(match_count, _num_sentence)
    recall = compute_recall(match_count, num_old_output_sentences)
    f1_score = compute_f1(precision, recall)

    label_filename.config(text="File Name: " + f"{file_name}")
    label_precision.config(text=f"{precision:.5f}")
    label_recall.config(text=f"{recall:.5f}")
    label_f1.config(text=f"{f1_score:.5f}")

    log_summary_to_excel(file_name, _num_sentence, num_old_output_sentences, match_count, precision, recall, f1_score)

    text_matched_sentences.config(state='normal')
    text_matched_sentences.delete(1.0, tk.END)
    text_matched_sentences.insert(tk.END, matched_text if match_count > 0 else "(Không có câu nào khớp)")
    text_matched_sentences.config(state='disabled')

    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, summary_document)
    text_old_output.delete(1.0, tk.END)
    text_old_output.insert(tk.END, old_output_text)

root = tk.Tk()
root.title("XML Text Summarizer")
root.state('zoomed')

style = ttk.Style(root)
style.theme_use('clam')

frame_top = ttk.Frame(root, padding=15)
frame_top.grid(row=0, column=0, sticky="ew")

label_num = ttk.Label(frame_top, text="Extracted No:", font=("Segoe UI", 11))
label_num.grid(row=0, column=0, sticky="w")

entry_num_sentence = ttk.Entry(frame_top, width=5, font=("Segoe UI", 11))
entry_num_sentence.insert(0, "10")
entry_num_sentence.grid(row=0, column=1, padx=(5, 25))

label_threshold = ttk.Label(frame_top, text="Threshold index (0-1):", font=("Segoe UI", 11))
label_threshold.grid(row=0, column=2, sticky="w")

entry_threshold = ttk.Entry(frame_top, width=6, font=("Segoe UI", 11))
entry_threshold.insert(0, "0.1")
entry_threshold.grid(row=0, column=3, padx=(5, 25))

# btn_select = ttk.Button(frame_top, text="Select input file", command=select_file)
# btn_select.grid(row=0, column=4)

style.configure("Custom.TButton", foreground="black", background="#add8e6")
style.map("Custom.TButton",
          background=[("active", "#87cefa"), ("!active", "#add8e6")])

btn_select = ttk.Button(frame_top, text="Select input file", command=select_file, style="Custom.TButton")
btn_select.grid(row=0, column=4)

frame_top.columnconfigure(4, weight=1)

frame_match = ttk.LabelFrame(root, text="Statistics", padding=10)
frame_match.grid(row=1, column=0, sticky="ew", padx=15, pady=(5,10))

label_filename = ttk.Label(frame_match, text="File Name:", font=("Segoe UI", 10, "bold"))
label_filename.grid(row=0, column=0, sticky="w", padx=(0, 15))

label_expected = create_info_pair(frame_match, "Expected:", "0", 1)
label_extracted = create_info_pair(frame_match, "Extracted:", "0", 2)
label_match_count = create_info_pair(frame_match, "Correct:", "0", 3)
label_precision = create_info_pair(frame_match, "Precision:", "0.00000", 4)
label_recall = create_info_pair(frame_match, "Recall:", "0.00000", 5)
label_f1 = create_info_pair(frame_match, "F1-score:", "0.00000", 6)

text_matched_sentences = tk.Text(frame_match, height=5, font=("Segoe UI", 10), bg="#eef5f9", state='disabled', wrap="word")
text_matched_sentences.grid(row=1, column=0, columnspan=7, sticky="ew", pady=(10, 0))

frame_match.columnconfigure(6, weight=1)

frame_bottom = ttk.Frame(root, padding=10)
frame_bottom.grid(row=2, column=0, sticky="nsew")
root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)
frame_bottom.columnconfigure(0, weight=1)
frame_bottom.columnconfigure(1, weight=1)
frame_bottom.rowconfigure(0, weight=1)

frame_summary = ttk.LabelFrame(frame_bottom, text="Summarizing data", padding=5)
frame_summary.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
frame_summary.rowconfigure(0, weight=1)
frame_summary.columnconfigure(0, weight=1)

text_output = tk.Text(frame_summary, wrap="word", font=("Segoe UI", 10))
text_output.grid(row=0, column=0, sticky="nsew")

scrollbar_out = ttk.Scrollbar(frame_summary, command=text_output.yview)
scrollbar_out.grid(row=0, column=1, sticky='ns')
text_output.config(yscrollcommand=scrollbar_out.set)

frame_old_output = ttk.LabelFrame(frame_bottom, text="Standard data", padding=5)
frame_old_output.grid(row=0, column=1, sticky="nsew")
frame_old_output.rowconfigure(0, weight=1)
frame_old_output.columnconfigure(0, weight=1)

text_old_output = tk.Text(frame_old_output, wrap="word", font=("Segoe UI", 10), bg="#f5f5f5")
text_old_output.grid(row=0, column=0, sticky="nsew")

scrollbar_old = ttk.Scrollbar(frame_old_output, command=text_old_output.yview)
scrollbar_old.grid(row=0, column=1, sticky='ns')
text_old_output.config(yscrollcommand=scrollbar_old.set)

root.mainloop()
