import pymupdf

doc = pymupdf.open("whisper.pdf") # open a document
out = open("output.txt", "wb") # create a text output

header = "Header"  # text in header
footer = "Page %i of %i"  # text in footer
for page in doc:
    page.insert_text((50, 50), header)  # insert header
    page.insert_text(  # insert footer 50 points above page bottom
        (50, page.rect.height - 50),
        footer % (page.number + 1, doc.page_count),
    )


for page in doc: # iterate the document pages
    text = page.get_text().encode("utf8") # get plain text (is in UTF-8)

    # tp = page.get_textpage_ocr()
    # text = page.get_text(textpage=tp)

    out.write(text) # write text of page
    out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
out.close()


