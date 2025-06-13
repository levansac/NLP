import tkinter as tk
from tkinter import ttk, messagebox
from summarizer_utils import (
    compute_tfidf_vectors,
    compute_cosine_similarity,
    get_graph,
    page_rank
)
from file_selector import get_file, log_summary_to_excel, get_sentences, compare_summaries
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
        messagebox.showerror("Error", "The value of threshold number is invalid.")
        return

    try:
        _num_sentence_percent = int(entry_num_sentence.get().strip())
        if not (0 <= _num_sentence_percent <= 100):
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "The value of extracted number is invalid.")
        return

    file_path, file_name = get_file()
    if not file_path:
        return

    sentences = get_sentences(file_path)
    count_sentence = len(sentences)
    if count_sentence == 0:
        messagebox.showinfo("Notification", "This file has no sentences to summarize.")
        return
    _num_sentence = 0
    _num_sentence = int(count_sentence*_num_sentence_percent/100)
    if _num_sentence > count_sentence:
        messagebox.showwarning("Warning",
            f"Number of summarizing sentences ({_num_sentence}) is greater than number of sentences in document ({count_sentence}). Automatically reduces to {count_sentence}.")
        _num_sentence = count_sentence

    old_output_file_path = file_path.replace("input", "output")
    old_output_sentences = get_sentences(old_output_file_path)
    num_old_output_sentences = len(old_output_sentences)
    if num_old_output_sentences == 0:
        messagebox.showinfo("Notification", "Teacher output file not found.")
        return

    # TF-IDF
    tfidf_vectors, _ = compute_tfidf_vectors(sentences)
    # Cosine
    cosine_sim_matrix = compute_cosine_similarity(tfidf_vectors)
    # graph
    graph = get_graph(sentences, cosine_sim_matrix, threshold=threshold)
    # page rank
    pagerank_scores = page_rank(graph, 0.85)

    ranked_sentences = sorted(((pagerank_scores[i], i) for i in range(count_sentence)), reverse=True)
    top_sentence_indices = [i for _, i in ranked_sentences[:_num_sentence]]
    top_sentence_indices.sort()

    summary_document = '\n'.join([sentences[i] for i in top_sentence_indices])
    old_output_text = '\n'.join(old_output_sentences)

    match_count, matched_text = compare_summaries(summary_document, old_output_sentences)

    label_extracted.config(text=f"{_num_sentence}")
    label_expected.config(text=f"{num_old_output_sentences}")
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
    text_matched_sentences.insert(tk.END, matched_text if match_count > 0 else "(There are no matching sentences.)")
    text_matched_sentences.config(state='disabled')

    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, summary_document)
    text_old_output.delete(1.0, tk.END)
    text_old_output.insert(tk.END, old_output_text)

import glob
import os

def run_all_files():
    folder_path = os.path.dirname(get_file()[0])

    # Lấy các file có đuôi .xml hoặc không có đuôi
    input_files = [f for f in glob.glob(os.path.join(folder_path, "*"))
                   if os.path.isfile(f) and (f.lower().endswith(".xml") or '.' not in os.path.basename(f))]

    if not input_files:
        messagebox.showinfo("Notification", "No input XML files or files without extension found in the folder.")
        return

    try:
        threshold = float(entry_threshold.get())
        if not (0 <= threshold <= 1):
            raise ValueError
    except:
        messagebox.showerror("Error", "The value of threshold number is invalid.")
        return

    try:
        _num_sentence_percent = int(entry_num_sentence.get().strip())
        if not (0 <= _num_sentence_percent <= 100):
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "The value of extracted number is invalid.")
        return

    count_total_files = len(input_files)
    count_processed = 0

    for idx, file_path in enumerate(input_files):
        try:
            file_name_current = os.path.basename(file_path)
            sentences = get_sentences(file_path)
            count_sentence = len(sentences)
            if count_sentence == 0:
                continue

            _num_sentence = int(count_sentence * _num_sentence_percent / 100)
            _num_sentence = min(_num_sentence, count_sentence)

            old_output_file_path = file_path.replace("input", "output")
            old_output_sentences = get_sentences(old_output_file_path)
            num_old_output_sentences = len(old_output_sentences)
            if num_old_output_sentences == 0:
                continue

            tfidf_vectors, _ = compute_tfidf_vectors(sentences)
            cosine_sim_matrix = compute_cosine_similarity(tfidf_vectors)
            graph = get_graph(sentences, cosine_sim_matrix, threshold=threshold)
            pagerank_scores = page_rank(graph, 0.85)

            ranked_sentences = sorted(((pagerank_scores[i], i) for i in range(count_sentence)), reverse=True)
            top_sentence_indices = [i for _, i in ranked_sentences[:_num_sentence]]
            top_sentence_indices.sort()

            summary_document = '\n'.join([sentences[i] for i in top_sentence_indices])
            match_count, matched_text = compare_summaries(summary_document, old_output_sentences)

            precision = compute_precision(match_count, _num_sentence)
            recall = compute_recall(match_count, num_old_output_sentences)
            f1_score = compute_f1(precision, recall)

            # Log kết quả ra Excel
            log_summary_to_excel(file_name_current, _num_sentence, num_old_output_sentences, match_count, precision, recall, f1_score)

            count_processed += 1

            # Update progress bar
            progress_percent = ((idx + 1) / count_total_files) * 100
            progress_var.set(progress_percent)
            root.update_idletasks()

        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            continue

    # Reset progress bar
    progress_var.set(0)
    messagebox.showinfo("Completed", f"Processed {count_processed}/{count_total_files} files.\nResults saved to Excel.")


root = tk.Tk()
root.title("XML Text Summarizer")
root.state('zoomed')

style = ttk.Style(root)
style.theme_use('clam')

# === Frame top ===
frame_top = ttk.Frame(root, padding=15)
frame_top.grid(row=0, column=0, sticky="ew")

# Frame con cho các label + entry (căn trái)
frame_entries = ttk.Frame(frame_top)
frame_entries.grid(row=0, column=0, sticky="w")

label_num = ttk.Label(frame_entries, text="Extracted (%):", font=("Segoe UI", 11))
label_num.grid(row=0, column=0, sticky="w")

entry_num_sentence = ttk.Entry(frame_entries, width=5, font=("Segoe UI", 11))
entry_num_sentence.insert(0, "10")
entry_num_sentence.grid(row=0, column=1, padx=(5, 15))

label_threshold = ttk.Label(frame_entries, text="Threshold index (0-1):", font=("Segoe UI", 11))
label_threshold.grid(row=0, column=2, sticky="w")

entry_threshold = ttk.Entry(frame_entries, width=6, font=("Segoe UI", 11))
entry_threshold.insert(0, "0.1")
entry_threshold.grid(row=0, column=3, padx=(5, 15))

label_damping = ttk.Label(frame_entries, text="Damping factor d (0-1):", font=("Segoe UI", 11))
label_damping.grid(row=0, column=4, sticky="w")

entry_damping = ttk.Entry(frame_entries, width=6, font=("Segoe UI", 11))
entry_damping.insert(0, "0.85")
entry_damping.grid(row=0, column=5, padx=(5, 15))

# Frame con cho buttons (căn phải)
frame_buttons = ttk.Frame(frame_top)
frame_buttons.grid(row=0, column=1, sticky="e")

style.configure("Custom.TButton", foreground="black", background="#add8e6")
style.map("Custom.TButton",
          background=[("active", "#87cefa"), ("!active", "#add8e6")])

btn_select = ttk.Button(frame_buttons, text="Select input file", command=select_file, style="Custom.TButton")
btn_select.grid(row=0, column=0, padx=(0, 5))

btn_run_all = ttk.Button(frame_buttons, text="Run all file", command=run_all_files, style="Custom.TButton")
btn_run_all.grid(row=0, column=1, padx=(0, 5))

# Cho frame_entries dãn ra, frame_buttons cố định
frame_top.columnconfigure(0, weight=1)
frame_top.columnconfigure(1, weight=0)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame_top, variable=progress_var, maximum=100)
progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))


# frame_top.columnconfigure(4, weight=1)

frame_match = ttk.LabelFrame(root, text="Statistics", padding=10)
frame_match.grid(row=1, column=0, sticky="ew", padx=15, pady=(5,10))

label_filename = ttk.Label(frame_match, text="File Name:", font=("Segoe UI", 10, "bold"))
label_filename.grid(row=0, column=0, sticky="w", padx=(0, 15))

label_extracted = create_info_pair(frame_match, "Extracted:", "0", 1)
label_expected = create_info_pair(frame_match, "Expected:", "0", 2)
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
