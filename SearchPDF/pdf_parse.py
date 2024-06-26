import fitz


def parse_pdf_to_text(pdf_file_path, output_file_path):
    document = fitz.open(pdf_file_path)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text = page.get_text()
            output_file.write(f"--- Page {page_num + 1}\n{text}\n")


def load_parsed_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text
