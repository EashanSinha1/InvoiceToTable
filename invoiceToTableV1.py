from PyPDF2 import PdfReader
from tabula import read_pdf
import pytesseract
from PIL import Image
import re
import json


def file_to_table(file_path):
    """Parses a file (PDF or image) and attempts to extract tables from it."""

    if file_path.lower().endswith('.pdf'):
        # Use PyPDF2 to extract text
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text()

        # Extract the invoice details
        invoice_details = extract_invoice_details_from_text(text)

        # Use tabula to extract tables
        tables = read_pdf(file_path, pages="all", multiple_tables=True)

    else:  # Assuming the file is an image
        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(Image.open(file_path))

        # Extract the invoice details
        invoice_details = extract_invoice_details_from_text(text)

        # Currently, there's no reliable method to extract tables from text
        # This would require additional processing and depends on the structure of the tables
        tables = None

    return invoice_details, tables


# def extract_invoice_details_from_text(text):
#     # Regular expressions for the invoice details
#     vendor_name_pattern = r"^(.*?)\n"  # Vendor name is the first line
#     # Date in the format DD/MM/YYYY
#     invoice_date_pattern = r"(Date\D*?)(\d{2}/\d{2}/\d{4})"
#     # Invoice number is a number
#     invoice_number_pattern = r"(Invoice\D*?)(\d+)"
#     # Total amount in the format X,XXX.XX
#     total_amount_pattern = r"(Balance Due\D*)([\d,]+\.\d{2})"

#     # This dictionary will hold the extracted invoice details
#     invoice_details = {}

#     # Extract the vendor name
#     vendor_name_match = re.search(vendor_name_pattern, text, re.MULTILINE)
#     if vendor_name_match:
#         invoice_details["Vendor Name"] = vendor_name_match.group(1).strip()

#     # Extract the invoice date
#     invoice_date_match = re.search(invoice_date_pattern, text)
#     if invoice_date_match:
#         invoice_details["Invoice Date"] = invoice_date_match.group(2)

#     # Extract the invoice number
#     invoice_number_match = re.search(invoice_number_pattern, text)
#     if invoice_number_match:
#         invoice_details["Invoice Number"] = invoice_number_match.group(
#             2).strip()

#     # Extract the total amount
#     total_amount_match = re.search(total_amount_pattern, text)
#     if total_amount_match:
#         invoice_details["Total Amount"] = total_amount_match.group(2)

#     return invoice_details

def extract_invoice_details_from_text(text):
    # Regular expressions for the invoice details
    vendor_name_pattern = r"^(.*?)\n"  # Vendor name is the first line
    # Date in formats like DD/MM/YYYY, D/M/YYYY, etc.
    invoice_date_pattern = r"(?i)(date.*?)(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
    # Invoice number is a number
    invoice_number_pattern = r"(?i)(invoice.*?)(\d+)"
    # Total amount in formats like X,XXX.XX
    total_amount_pattern = r"(?i)(total.*?)([\d,]+\.\d{2})"

    # This dictionary will hold the extracted invoice details
    invoice_details = {}

    # Extract the vendor name
    vendor_name_match = re.search(vendor_name_pattern, text, re.MULTILINE)
    if vendor_name_match:
        invoice_details["Vendor Name"] = vendor_name_match.group(1).strip()

    # Extract the invoice date
    invoice_date_match = re.search(invoice_date_pattern, text)
    if invoice_date_match:
        invoice_details["Invoice Date"] = invoice_date_match.group(2)

    # Extract the invoice number
    invoice_number_match = re.search(invoice_number_pattern, text)
    if invoice_number_match:
        invoice_details["Invoice Number"] = invoice_number_match.group(
            2).strip()

    # Extract the total amount
    total_amount_match = re.search(total_amount_pattern, text)
    if total_amount_match:
        invoice_details["Total Amount"] = total_amount_match.group(2)

    return invoice_details


if __name__ == "__main__":
    invoice_details, tables = file_to_table("invoice_example.pdf")
    print("Invoice Details:")
    for key, value in invoice_details.items():
        print(f"{key}: {value}")
    print("\nTables:")
    if tables is not None:
        for i, table in enumerate(tables):
            print(f"Table {i+1}:")
            print(table)

# if __name__ == "__main__":
#     invoice_details, tables = file_to_table("invoice_example.pdf")
#     print(invoice_details)

#     # Write the invoice details to a JSON file
#     with open('invoice_details.json', 'w') as f:
#         json.dump(invoice_details, f)
