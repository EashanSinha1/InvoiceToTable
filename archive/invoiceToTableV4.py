import sys
import os
import json
import re
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path
import pandas as pd
import tabula

# Your previous code for handling PDFs goes here


def pdf_to_table(pdf_file_path):
    text = ""
    tables = None
    with pdfplumber.open(pdf_file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
            tables = tabula.read_pdf(
                pdf_file_path, pages="all", multiple_tables=True)
    return text, tables

# Your previous code for handling images goes here


def extract_invoice_details_from_text(text):
    # Define regex patterns to find desired fields
    vendor_name_pattern = r"^(.*?)\n"
    invoice_date_pattern = r"(?i)(invoice date:)(.*?)(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
    invoice_number_pattern = r"(?i)(invoice no:)(.*?)(\d+)"
    total_amount_pattern = r"(?i)(balance due)(.*?)([\d,]+\.\d{2})"

    # Dictionary to hold the invoice details
    invoice_details = {}

    # Extract vendor name
    vendor_name_match = re.search(vendor_name_pattern, text, re.MULTILINE)
    if vendor_name_match:
        invoice_details["Vendor Name"] = vendor_name_match.group(1).strip()

    # Extract invoice date
    invoice_date_match = re.search(invoice_date_pattern, text)
    if invoice_date_match:
        invoice_details["Invoice Date"] = invoice_date_match.group(3)

    # Extract invoice number
    invoice_number_match = re.search(invoice_number_pattern, text)
    if invoice_number_match:
        invoice_details["Invoice Number"] = invoice_number_match.group(
            3).strip()

    # Extract total amount
    total_amount_match = re.search(total_amount_pattern, text)
    if total_amount_match:
        invoice_details["Total Amount"] = total_amount_match.group(3)

    return invoice_details

# Check file extension and process accordingly


def file_to_table(file_path):
    filename, file_extension = os.path.splitext(file_path)
    if file_extension.lower() in ['.jpg', '.jpeg', '.png']:
        # Use OCR to extract the text from the image
        text = pytesseract.image_to_string(Image.open(file_path))
        # Extract the invoice details
        invoice_details = extract_invoice_details_from_text(text)
        return invoice_details, None
    elif file_extension.lower() == '.pdf':
        # Extract text and tables from PDF
        text, tables = pdf_to_table(file_path)
        # Extract the invoice details
        invoice_details = extract_invoice_details_from_text(text)
        return invoice_details, tables
    else:
        print(f"Unsupported file type: {file_extension}")
        return None, None


def write_to_json(file_path, data):
    # Make sure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Write the data to a JSON file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    # Get the input file path from the command-line arguments
    input_file_path = sys.argv[1]
    # Define the output file path
    output_file_path = os.path.join("jsons", os.path.splitext(
        os.path.basename(input_file_path))[0] + ".json")

    # Extract the invoice details
    invoice_details, tables = file_to_table(input_file_path)

    # Print the invoice details
    print("Invoice Details:")
    print(invoice_details)

    if tables is not None:
        print("\nTables:")
        for i, table in enumerate(tables, start=1):
            print(f"Table {i}:")
            print(table)

    # Write the invoice details to a JSON file
    write_to_json(output_file_path, invoice_details)
