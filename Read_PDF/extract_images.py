import pymupdf
from pprint import pprint

doc = pymupdf.open("whisper.pdf") # open a document

# locate and extract any tables on page
# display number of found tables

for page_index in range(len(doc)):
    page = doc[page_index] 
    tabs = page.find_tables() 
    print(f"{len(tabs.tables)} found on {page}") 

    if tabs.tables:  # at least one table found?
        pprint(tabs[0].extract())  # print content of first table



for page_index in range(len(doc)): # iterate over pdf pages
    page = doc[page_index] # get the page
    image_list = page.get_images()

    table = page.find_tables()

    # print the number of images found on the page
    if image_list:
        print(f"Found {len(image_list)} images on page {page_index}")
    else:
        print("No images found on page", page_index)

    for image_index, img in enumerate(image_list, start=1): # enumerate the image list
        xref = img[0] # get the XREF of the image
        pix = pymupdf.Pixmap(doc, xref) # create a Pixmap

        if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

        pix.save("page_%s-image_%s.png" % (page_index, image_index)) # save the image as png
        pix = None