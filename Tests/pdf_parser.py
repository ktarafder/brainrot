#pip install PyPDF2
import PyPDF2

def parse_pdf(file_path):    
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num, page in enumerate(reader.pages):
            text += page.extract_text() +  "\n\n"
        return text  
    

print(parse_pdf("Tests/Files/brainrot.pdf"))