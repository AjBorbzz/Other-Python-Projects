from pathlib import Path
from PIL import Image, ImageOps 
import argparse 
import re 


def natural_sort_key(path: Path): 
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]

def jpg_folder_to_pdf(input_folder: Path, output_pdf: Path): 
    image_files = sorted(
        [
            file 
            for file in input_folder.iterdir()
            if file.is_file() and file.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ],
        key=natural_sort_key,
    )

    if not image_files:
        raise FileNotFoundError(
            f"No JPG Files found in: {input_folder}"
        )
    
    images = []

    try:
        for image_file in image_files:
            with Image.open(image_file) as source:
                image = ImageOps.exif_transpose(source)

                if image.mode != "RGB":
                    image = image.convert("RGB")
                else:
                    image = image.copy()

                images.append(image)

        first_image, *remaining_images = images 

        first_image.save(
            output_pdf,
            "PDF",
            save_all=True,
            append_images=remaining_images,
            resolution=100,
        )

        print(f"Created: {output_pdf}")
        print(f"Pages: {len(images)}")

    finally:
        for image in images:
            image.close()


def main():
    parser = argparse.ArgumentParser(
        description="Combine JPG files from a folder into one PDF."
    )
    parser.add_argument("input_folder", type=Path)
    parser.add_argument("output_pdf", type=Path)
    args = parser.parse_args()

    if not args.input_folder.is_dir():
        raise NotADirectoryError(
            f"Folder does not exist: {args.input_folder}"
        )
    
    jpg_folder_to_pdf(
        args.input_folder.resolve(),
        args.output_pdf.resolve()
    )


if __name__ == "__main__":
    main()