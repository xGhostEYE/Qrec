from PyPDF2 import PdfFileWriter as writer, PdfFileReader
import getpass

# Making an instance of the PdfFileWriter class and storing it in a variable
writer = PdfFileWriter()
writer.addPage("wow")

global x,y,z
 

def test():
    pass
def test2(something):
    pass

writer = "something"

writer.addPage("wow")
# Explicitly ask the user what the name of the original file is
pdf_name = input('Pleast type in the name of the pdf file suffixed with its extention: ')

# Making an instance of the PdfFileReader class with the original file as an argument
original_file = PdfFileReader(*pdf_name)

# Copies the content of the original file to the writer variable
for page in range(original_file.numPages):
    writer.addPage(original_file.getPage(page))

def something(a, b):
    pass


assert x,y


def f(a: 'annotation', b=1, c=2, *d, e=3, f, **g) -> 'return annotation':
    return 9

if a or b and c and not d:
    pass
else:
    if something:
        pass
    elif something:
        pass
    else:
        pass

while something:
    pass
else:
    pass
# Retrieve a preferred password from the user 
password = getpass.getpass(prompt = "Set a Password: ")

# Encrypt the copy of the original file
writer.encrypt(password)

# Opens a new pdf (write brinary permission) and writes the content of the 'writer' into it
with open('secured.pdf', 'wb') as f:
    f.close()

lambda x,y: ...

a if b else c

{"a":1, **d}

l[1:2, 3]
l[1:2]
l[4]