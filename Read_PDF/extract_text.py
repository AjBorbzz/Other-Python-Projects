import pymupdf

doc = pymupdf.open("whisper.pdf") # open a document
out = open("output.txt", "wb") # create a text output

for page in doc: # iterate the document pages
    text = page.get_text().encode("utf8") # get plain text (is in UTF-8)

    tp = page.get_textpage_ocr()
    text = page.get_text(textpage=tp)

    out.write(text) # write text of page
    out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
out.close()