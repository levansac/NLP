import os
from tkinter import filedialog
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import string
from tkinter import messagebox

def get_file():
    # Select file
    file_path = filedialog.askopenfilename(
        title="Select file",
        filetypes=[("All files", "*.*")]
    )

    if not file_path:
        return None, None

    # Get file name
    file_name = os.path.basename(file_path)

    return  file_path, file_name



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
        messagebox.showerror("Error", f"An error occurred while reading the file.:\n{e}")

def preprocess_sentence(sentence):
    # Loại bỏ dấu câu, chuyển về chữ thường, và strip
    sentence = sentence.lower().strip()
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    return sentence

def compare_summaries_cosine(summary_document, old_output_sentences, threshold=0.7):
    summary_sentences = summary_document.strip().split('\n')
    summary_sentences = [preprocess_sentence(s) for s in summary_sentences if s.strip()]
    old_output_sentences = [preprocess_sentence(s) for s in old_output_sentences if s.strip()]

    matched_sentences = []

    for sum_sent in summary_sentences:
        for old_sent in old_output_sentences:
            vectorizer = TfidfVectorizer().fit([sum_sent, old_sent])
            vecs = vectorizer.transform([sum_sent, old_sent])
            sim = cosine_similarity(vecs[0], vecs[1])[0][0]
            if sim >= threshold:
                matched_sentences.append(sum_sent)
                break  # Một câu chỉ cần khớp một câu là đủ

    match_count = len(matched_sentences)
    matched_text = '.\n'.join(matched_sentences) if match_count > 0 else ''
    return match_count, matched_text

def log_summary_to_excel(file_name, num_summary_sentences, num_reference_sentences, match_count, precision, recall,f1_score):
    """
    Ghi log kết quả tóm tắt vào file Excel (.xlsx).
    """

    # Đường dẫn thư mục document cùng cấp file hiện tại
    base_dir = os.path.dirname(os.path.abspath(__file__))
    document_folder = os.path.join(base_dir, "document")
    os.makedirs(document_folder, exist_ok=True)  # Tạo nếu chưa có

    log_file = os.path.join(document_folder, "summary_log.xlsx")

    # log_file = "document/summary_log.xlsx"
    headers = ["Action Time", "File Name", "Extracted", "Expected", "Correct", "Precision", "Recall", "F1-Score"]

    if not os.path.exists(log_file):
        wb = Workbook()
        ws = wb.active
        ws.append(headers)
    else:
        wb = load_workbook(log_file)
        ws = wb.active

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        file_name,
        num_summary_sentences,
        num_reference_sentences,
        match_count,
        round(precision, 5),
        round(recall, 5),
        round(f1_score, 5)
    ]
    ws.append(row)

    # Optional: auto adjust column width
    for col in ws.columns:
        max_length = 0
        column = get_column_letter(col[0].column)
        for cell in col:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 2

    try:
        wb.save(log_file)
    except Exception as e:
        print(f"Lỗi ghi file Excel: {e}")
