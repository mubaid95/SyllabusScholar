import fitz  # PyMuPDF
import easyocr

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Function to extract text from image using EasyOCR
def extract_text_from_image_easyocr(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)

    extracted_text_lines = []
    for detection in result:
        text = detection[1]  # Extracting the text from each detection
        extracted_text_lines.append(text)

    return extracted_text_lines

# Function to split text into lines
def text_to_lines(text):
    lines = text.split('\n')
    return lines
