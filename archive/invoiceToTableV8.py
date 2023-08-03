import sys
import os
import json
import re
from tabula import read_pdf
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import img2pdf
import cv2
import numpy as np


def extract_invoice_details_from_text(text):
    vendor_name_pattern = r"From:\s*([^\n]+)"
    invoice_date_pattern = r"(?i)(invoice.*date.*?)(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|[a-z]+ \d{1,2}, \d{2,4})"
    invoice_number_pattern = r"(?i)(invoice.*number.*?)([\w-]+)"
    total_amount_pattern = r"(?i)(total.*?due.*?)([\d,]+\.\d{2})"

    invoice_details = {}

    vendor_name_match = re.search(vendor_name_pattern, text)
    invoice_details["Vendor Name"] = vendor_name_match.group(
        1).strip() if vendor_name_match else "Not Found"

    invoice_date_match = re.search(invoice_date_pattern, text)
    invoice_details["Invoice Date"] = invoice_date_match.group(
        2) if invoice_date_match else "Not Found"

    invoice_number_match = re.search(invoice_number_pattern, text)
    invoice_details["Invoice Number"] = invoice_number_match.group(
        2).strip() if invoice_number_match else "Not Found"

    total_amount_match = re.search(total_amount_pattern, text)
    invoice_details["Total Amount"] = total_amount_match.group(
        2) if total_amount_match else "Not Found"

    return invoice_details


def file_to_table(file_path):
    if file_path.lower().endswith('.pdf'):
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        invoice_details = extract_invoice_details_from_text(text)
        tables = read_pdf(file_path, pages="all", multiple_tables=True)
    else:  # Assuming the file is an image
        image = cv2.imread(file_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        ret, thresh = cv2.threshold(
            blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(thresh, config='--psm 6')
        invoice_details = extract_invoice_details_from_text(text)
        tables = None
    return invoice_details, tables


def write_to_json(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    input_file_path = sys.argv[1]
    output_file_path = os.path.join("jsons", os.path.splitext(
        os.path.basename(input_file_path))[0] + ".json")

    invoice_details, tables = file_to_table(input_file_path)

    print("Invoice Details:")
    print(invoice_details)

    print("\nTables:")
    if tables is not None:
        tables_as_dict = [table.to_dict('split') for table in tables]
        for i, table_dict in enumerate(tables_as_dict, 1):
            print(f"Table {i}:")
            print(table_dict['data'])
    else:
        tables_as_dict = []

    data = {
        "Invoice Details": invoice_details,
        "Tables": tables_as_dict
    }

    write_to_json(output_file_path, data)
