
## JPG To PDF Converter

A Simple Python utility that combines ordered .jpg or .jpeg into a single PDF file

#### Install Dependency
```bash
pip install Pillow
```

### Usage
```bash
python main.py "<Target Folder>" "<Outputfile>"
```

example:
```bash
python main.py "Gundam Hobby Life 001" "GHL_PDF_001.pdf"
```

The combined PDF will be created

#### Notes:
* Supports .jpg and .jpeg files.
* Uses natural filename sorting to preserve page order.
* Corrects image orientation from EXIF metadata.
* Converts images to RGB for PDF compatibility.
