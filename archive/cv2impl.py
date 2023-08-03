import cv2
import numpy as np
import pytesseract
import pandas as pd


def parse_image(image_path):
    """Parses an image of a F&B invoice and returns the data in a table format."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image at {image_path}")
            return None

        grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Use adaptive thresholding
        thresholded_image = cv2.adaptiveThreshold(grayscale_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                  cv2.THRESH_BINARY, 11, 2)

        # Find the table in the image
        table_coordinates = find_table(thresholded_image)

        # Extract the data from the table
        table_data = extract_data_from_table(
            thresholded_image, table_coordinates)

        # Convert the list of lists to a pandas DataFrame
        table_data = pd.DataFrame(table_data)

        return table_data

    except Exception as e:
        print(f"Failed to parse image {image_path} with error {e}")
        raise e


def find_table(image):
    """Finds the table in an image of a F&B invoice."""

    table_dimensions = (100, 100)
    table_threshold = 0.2

    contours, _ = cv2.findContours(
        image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

    tables = [contour for contour in contours if cv2.contourArea(
        contour) > table_dimensions[0] * table_dimensions[1] * table_threshold]

    return tables


def extract_data_from_table(image, table_coordinates):
    """Extracts the data from a table in an image of a F&B invoice."""
    table_data = []
    for table in table_coordinates:
        x, y, w, h = cv2.boundingRect(table)
        table_img = image[y:y+h, x:x+w]

        # Here, you can add some image processing steps if needed, for example:
        # - Binarization to make the image black and white
        # - Noise removal
        # - Skew correction

        # You can use cv2.findContours again to find the rows in the table
        contours, _ = cv2.findContours(
            table_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Here, you might want to sort the contours top to bottom, based on their y-coordinate

        # Then you can loop through each contour (row) and extract the data
        for row in contours:
            x, y, w, h = cv2.boundingRect(row)
            row_img = table_img[y:y+h, x:x+w]

            # You can use cv2.findContours again to find the cells in the row
            cell_contours, _ = cv2.findContours(
                row_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Here, you might want to sort the cell_contours left to right, based on their x-coordinate

            # Then you can loop through each cell_contour and extract the text
            row_data = []
            for cell in cell_contours:
                x, y, w, h = cv2.boundingRect(cell)
                cell_img = row_img[y:y+h, x:x+w]
                cell_text = pytesseract.image_to_string(cell_img)
                row_data.append(cell_text)

            table_data.append(row_data)

    return table_data


def extract_row_data(image, row_coordinates):
    """Extracts the data from a row in a table in an image of a F&B invoice."""

    row_data = []

    for coordinate in row_coordinates:
        x, y, w, h = coordinate
        cell_image = image[y:y + h, x:x + w]
        cell_text = pytesseract.image_to_string(cell_image)
        row_data.append(cell_text)

    return row_data


if __name__ == "__main__":
    table_data = parse_image("invoice.jpg")
    print(table_data)
