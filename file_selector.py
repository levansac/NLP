import os
from tkinter import filedialog
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
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

def compare_summaries(summary_document, old_output_sentences):
    # Tách câu
    summary_sentences = summary_document.strip().split('\n')
    summary_sentences = [preprocess_sentence(s) for s in summary_sentences if s.strip()]

    # DISTINCT summary_sentences
    from collections import OrderedDict
    summary_sentences = list(OrderedDict.fromkeys(summary_sentences))

    # Xử lý old output
    old_output_sentences = [preprocess_sentence(s) for s in old_output_sentences if s.strip()]
    old_output_set = set(old_output_sentences)

    # So sánh
    matched_sentences = [s for s in summary_sentences if s in old_output_set]
    match_count = len(matched_sentences)

    if match_count > 0:
        matched_text = '\n'.join(matched_sentences)
    else:
        matched_text = ''

    return match_count, matched_text



