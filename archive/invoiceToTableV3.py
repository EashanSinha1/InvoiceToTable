import sys
import os
import json
from tabula import read_pdf
from PyPDF2 import PdfReader
import re
import pytesseract
from PIL import Image


def extract_invoice_details_from_text(text):
    # Define regex patterns to find desired fields
    vendor_name_pattern = r"^(.*?)\n"
    invoice_date_pattern = r"(?i)(date.*?)(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
    invoice_number_pattern = r"(?i)(invoice.*?)(\d+)"
    total_amount_pattern = r"(?i)(total.*?)([\d,]+\.\d{2})"

    # Dictionary to hold the invoice details
    invoice_details = {}

    # Extract vendor name
    vendor_name_match = re.search(vendor_name_pattern, text, re.MULTILINE)
    if vendor_name_match:
        invoice_details["Vendor Name"] = vendor_name_match.group(1).strip()

    # Extract invoice date
    invoice_date_match = re.search(invoice_date_pattern, text)
    if invoice_date_match:
        invoice_details["Invoice Date"] = invoice_date_match.group(2)

    # Extract invoice number
    invoice_number_match = re.search(invoice_number_pattern, text)
    if invoice_number_match:
        invoice_details["Invoice Number"] = invoice_number_match.group(
            2).strip()

    # Extract total amount
    total_amount_match = re.search(total_amount_pattern, text)
    if total_amount_match:
        invoice_details["Total Amount"] = total_amount_match.group(2)

    return invoice_details


def file_to_table(file_path):
    # Check if the file is a PDF
    if file_path.lower().endswith('.pdf'):
        # Open the PDF file
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            text = ""
            # Extract the text from each page of the PDF
            for page in pdf.pages:
                text += page.extract_text()
        # Extract the invoice details
        invoice_details = extract_invoice_details_from_text(text)
        # Extract the tables
        tables = read_pdf(file_path, pages="all", multiple_tables=True)
    else:  # Assuming the file is an image
        # Use OCR to extract the text from the image
        text = pytesseract.image_to_string(Image.open(file_path))
        # Extract the invoice details
        invoice_details = extract_invoice_details_from_text(text)
        # Set tables to None since we cannot extract tables from an image
        tables = None
    return invoice_details, tables


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

    # Extract the invoice details and tables
    invoice_details, tables = file_to_table(input_file_path)

    # Print the invoice details
    print("Invoice Details:")
    print(invoice_details)

    # Print the tables
    print("\nTables:")

    # If tables is not None, convert each table from a DataFrame to a dictionary
    if tables is not None:
        tables_as_dict = [table.to_dict('records') for table in tables]
    else:  # If tables is None, set tables_as_dict to an empty list
        tables_as_dict = []

    # Print each table
    for i, table in enumerate(tables_as_dict, 1):
        print(f"Table {i}:")
        print(table)

    # Combine the invoice details and tables into one dictionary
    data = {
        "Invoice Details": invoice_details,
        "Tables": tables_as_dict
    }

    # Write the combined data to a JSON file
    write_to_json(output_file_path, data)
