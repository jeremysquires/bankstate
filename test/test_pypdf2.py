from PyPDF2 import PdfReader

# creating a pdf file object
pdfObject = open('./data/bmo_chq_eStatement_2022-11-04.pdf', 'rb')

# creating a pdf reader object
pdfReader = PdfReader(pdfObject)

# Extract and concatenate each page's content
text=''
for i in range(0,len(pdfReader.pages)):
    # creating a page object
    pageObject = pdfReader.pages[i]
    # extracting text from page
    text += pageObject.extract_text()
print(text)

'''
Numbers are preceded by slash, special chars are encoded
/2c = , - /2e = . - etc.
Nov /0/6 Opening balance /2/2c/0/0/0/2e/0/0
Nov /0/8 Online Bill Payment/2c HEAT /2/0/0/2e/0/0 /2/2c/1/2e/8/0/0/2e/0/0
'''