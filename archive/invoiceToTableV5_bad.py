import re
import json
import sys
import os
from tabula.io import read_pdf
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract


def pdf_to_text(pdf_path):
    """
    Convert pdf content to text using OCR
    """
    images = convert_from_path(pdf_path)
    text = pytesseract.image_to_string(images[0])
    return text


def pdf_to_table(pdf_path):
    """
    Extract tables from the pdf
    """
    tables = read_pdf(pdf_path, pages="all", multiple_tables=True)
    return tables


def extract_invoice_details(text, tables):
    """
    Extracts vendor name, invoice number, invoice date, and total amount from the given text.
    """
    vendor_name = re.search(r"From:\s*([^\n]+)", text)
    invoice_number = re.search(
        r"Invoice Number:\s*(\S+)|Invoice\s*(\S+)", text)
    invoice_date = re.search(
        r"Invoice Date:\s*([^\n]+)|Date:\s*([^\n]+)", text)
    total_due = re.search(
        r"Total Due:\s*\$([^\n]+)|Total:\s*\$([^\n]+)|Balance Due:\s*\$([^\n]+)", text)

    # Calculate total amount from tables if not found in text
    if total_due is None:
        for table in tables:
            if "Total" in table.columns:
                total_due = table["Total"].str.extract(
                    r"\$(.*)").astype(float).sum()

    invoice_details = {
        "Vendor Name": vendor_name.group(1) if vendor_name else "Not Found",
        "Invoice Number": invoice_number.group(1) if invoice_number else "Not Found",
        "Invoice Date": invoice_date.group(1) if invoice_date else "Not Found",
        "Total Amount": total_due.group(1) if total_due else "Not Found"
    }

    return invoice_details


def table_to_json(table):
    """
    Convert a dataframe to a list of dicts
    """
    return table.to_dict('records')


def main(input_file_path):
    if input_file_path.endswith('.pdf'):
        text = pdf_to_text(input_file_path)
        tables = pdf_to_table(input_file_path)
    else:  # it's an image
        text = pytesseract.image_to_string(Image.open(input_file_path))
        tables = None

    invoice_details = extract_invoice_details(text)

    print("Invoice Details:")
    print(invoice_details)

    print("\nTables:")
    if tables is not None:
        for i, table in enumerate(tables, start=1):
            print(f"Table {i}:")
            print(table)

    # Convert the tables to a list of dicts
    tables_as_dict = [table_to_json(table)
                      for table in tables] if tables else []

    # Prepare the final dict
    result = {
        'Invoice Details': invoice_details,
        'Tables': tables_as_dict
    }

    # Convert the dict to a JSON and save it
    json_path = os.path.join(
        'jsons', os.path.basename(input_file_path) + '.json')
    with open(json_path, 'w') as json_file:
        json.dump(result, json_file, indent=4)


if __name__ == "__main__":
    main(sys.argv[1])
