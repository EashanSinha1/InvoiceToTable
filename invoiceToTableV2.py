import json
from tabula import read_pdf
from PyPDF2 import PdfReader
import re
import pytesseract
from PIL import Image


def extract_invoice_details_from_text(text):
    vendor_name_pattern = r"^(.*?)\n"
    invoice_date_pattern = r"(?i)(date.*?)(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
    invoice_number_pattern = r"(?i)(invoice.*?)(\d+)"
    total_amount_pattern = r"(?i)(total.*?)([\d,]+\.\d{2})"

    invoice_details = {}

    vendor_name_match = re.search(vendor_name_pattern, text, re.MULTILINE)
    if vendor_name_match:
        invoice_details["Vendor Name"] = vendor_name_match.group(1).strip()

    invoice_date_match = re.search(invoice_date_pattern, text)
    if invoice_date_match:
        invoice_details["Invoice Date"] = invoice_date_match.group(2)

    invoice_number_match = re.search(invoice_number_pattern, text)
    if invoice_number_match:
        invoice_details["Invoice Number"] = invoice_number_match.group(
            2).strip()

    total_amount_match = re.search(total_amount_pattern, text)
    if total_amount_match:
        invoice_details["Total Amount"] = total_amount_match.group(2)

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
        text = pytesseract.image_to_string(Image.open(file_path))
        invoice_details = extract_invoice_details_from_text(text)
        tables = None

    return invoice_details, tables


def write_to_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    invoice_details, tables = file_to_table("invoice_example.pdf")
    print("Invoice Details:")
    print(invoice_details)
    print("\nTables:")

    # Convert the tables from DataFrame to dict for JSON serialization
    tables_as_dict = [table.to_dict('records') for table in tables]

    for i, table in enumerate(tables_as_dict, 1):
        print(f"Table {i}:")
        print(table)

    # Combine the invoice details and tables into one dictionary
    data = {
        "Invoice Details": invoice_details,
        "Tables": tables_as_dict
    }

    # Write the combined data to a JSON file
    write_to_json('invoice_data.json', data)
