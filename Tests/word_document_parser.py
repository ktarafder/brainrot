#pip install python-docx
from docx import Document

def parse_word(file_path):
    document = Document(file_path)
    text = ""
    for i, paragraph in enumerate(document.paragraphs):
        text += paragraph.text + "\n\n"
    print(text)

parse_word("Tests/Files/brainrot.docx")