from pypdf import PdfReader
import utils

# TODO: read commmand line file name
def get_filename():
    filename = "./test/data/bmo_chq_eStatement_2022-11-04.pdf"
    return filename

def get_raw_text_lines(filename):
    pdfObject = open(filename, 'rb')
    pdfReader = PdfReader(pdfObject)
    text_lines=[]
    for pageObject in pdfReader.pages:
        page = pageObject.extract_text()
        text_lines.extend(page.split("\n"))
    return text_lines

filename = get_filename()
raw_text_lines = get_raw_text_lines(filename)
transaction_lines = filter(utils.is_transaction_line, raw_text_lines)

'''
Numbers are preceded by slash, special chars are encoded
/2c = , - /2e = . - etc.
Nov /0/6 Opening balance /2/2c/0/0/0/2e/0/0
Nov /0/8 Online Bill Payment/2c HEAT /2/0/0/2e/0/0 /2/2c/1/2e/8/0/0/2e/0/0
'''
