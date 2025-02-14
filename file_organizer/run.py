import os
from pathlib import Path 

DIRECTORIES = {
    "HTML": [".html5", ".html", ".htm", ".xhtml"],
    "IMAGES": [".jpeg", ".jpg", ".tiff", ".hec", ".gif", ".bmp", ".png", ".bpg",
               ".svg", ".heif", ".psd"],
    "VIDEOS": [".avi", ".flv", ".wmv", ".mov", ".mp4", ".webm", ".vob", ".mng",
               ".qt", ".mpg", ".mpeg", ".3gp", ".mkv"],
    "DOCUMENTS": [".oxps", ".epub", ".pages", ".docx", ".doc", ".fdf", ".ods",
                  ".odt", ".pwi", ".xsn", ".xps", ".dotx", ".docm", ".dox",
                  ".rvg", ".rtf", ".rtfd", ".wpd", ".xls", ".xlsx", ".ppt",
                  "pptx"],
    "ARCHIVES": [".a", ".ar", ".cpio", ".iso", ".tar", ".gz", ".rz", ".7z",
                 ".dmg", ".rar", ".xar", ".zip"],
    "AUDIO": [".aac", ".aa", ".aac", ".dvf", ".m4a", ".m4b", ".m4p", ".mp3",
              ".msv", "ogg", "oga", ".raw", ".vox", ".wav", ".wma"],
    "PLAINTEXT": [".txt", ".in", ".out"],
    "PDF": [".pdf"],
    "PYTHON": [".py"],
    "XML": [".xml"],
    "EXE": [".exe"],
    "SHELL": [".sh"]
}

FILE_FORMATS = {file_format: directory for directory, file_formats in DIRECTORIES.items()
                  for file_format in file_formats}

def organize_files(source_directory):
    """
    Organizes files in the specified source directory based on their file extensions.

    Args:
        source_directory: The path to the source directory as a string.
    """
    source_dir = Path(source_directory)

    for entry in source_dir.iterdir():
        if entry.is_file():
            file_format = entry.suffix.lower()
            if file_format in FILE_FORMATS:
                directory_path = source_dir / FILE_FORMATS[file_format]
                directory_path.mkdir(exist_ok=True)
                entry.rename(directory_path / entry.name)

    # Create "OTHER" directory to move files with unknown extensions
    other_dir = source_dir / "OTHER"
    other_dir.mkdir(exist_ok=True)

    for entry in source_dir.iterdir():
        if entry.is_file() and entry.suffix.lower() not in FILE_FORMATS:
            entry.rename(other_dir / entry.name)

    # Remove empty directories (except "OTHER")
    for entry in source_dir.iterdir():
        if entry.is_dir() and entry != other_dir and not any(entry.iterdir()):
            entry.rmdir()

def get_download_dir():
    home = Path.home()
    downloads = home / 'Downloads'
    return downloads


if __name__ == '__main__':
    download_directory = get_download_dir()
    organize_files(download_directory)
