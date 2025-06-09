import os
from tkinter import filedialog
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter

def get_file():
    # Chọn file
    file_path = filedialog.askopenfilename(
        title="Chọn file",
        filetypes=[("All files", "*.*")]
    )

    if not file_path:
        return None, None

    # Lấy tên file
    file_name = os.path.basename(file_path)

    return  file_path, file_name

def compare_summaries(summary_document, old_output_sentences):
    # Tiền xử lý câu: tách, chuẩn hóa
    summary_sentences = summary_document.split('. ')
    summary_sentences = [s.strip().lower() for s in summary_sentences if s.strip()]
    old_output_set = set([s.strip().lower() for s in old_output_sentences if s.strip()])

    # So sánh
    matched_sentences = [s for s in summary_sentences if s in old_output_set]
    match_count = len(matched_sentences)


    # Hiển thị kết quả
    if match_count > 0:
        matched_text = '\n\n'.join(matched_sentences)
    else:
        matched_text = ''
    return match_count, matched_text



def log_summary_to_excel(file_name, num_summary_sentences, num_reference_sentences, match_count, precision, recall):
    """
    Ghi log kết quả tóm tắt vào file Excel (.xlsx).
    """

    # Đường dẫn thư mục document cùng cấp file hiện tại
    base_dir = os.path.dirname(os.path.abspath(__file__))
    document_folder = os.path.join(base_dir, "document")
    os.makedirs(document_folder, exist_ok=True)  # Tạo nếu chưa có

    log_file = os.path.join(document_folder, "summary_log.xlsx")

    # log_file = "document/summary_log.xlsx"
    headers = ["Action Time", "File Name", "Extracted", "Expected", "Correct", "Precision", "Recall"]

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
        round(recall, 5)
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

    wb.save(log_file)
