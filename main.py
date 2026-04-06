import os
import re
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path

# -------------------------------
# CONFIG
# -------------------------------
INPUT_PDF = "input_pdfs/tnpsc.pdf"
OUTPUT_TEXT = "ocr_text/output.txt"
SAVE_IMAGES = False  # set True if you want debug images
IMAGE_DIR = "images"

# Tesseract config
TESS_CONFIG = "--oem 3 --psm 6"
LANG = "eng"  # requires Tamil installed


# -------------------------------
# STEP 1: PDF → Images
# -------------------------------
from pdf2image import convert_from_path
import os

def pdf_to_images(pdf_path, dpi=400):
    print("[INFO] Converting PDF to images...")

    pages = convert_from_path(pdf_path, dpi=dpi)

    return pages


# -------------------------------
# STEP 2: Preprocess Image
# -------------------------------
def preprocess_image(pil_image):
    img = np.array(pil_image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # OTSU threshold (no blur)
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return thresh


# -------------------------------
# STEP 3: OCR Extraction
# -------------------------------
def extract_text(image):
    text = pytesseract.image_to_string(
        image,
        lang=LANG,
        config=TESS_CONFIG
    )
    return text


# -------------------------------
# STEP 4: Clean Text
# -------------------------------
def clean_text(text):
    # Remove extra spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Fix multiple newlines
    text = re.sub(r'\n+', '\n', text)

    # Remove weird characters (optional tuning)
    text = re.sub(r'[^\x00-\x7F\u0B80-\u0BFF\n ]+', '', text)

    return text.strip()


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def ocr_pipeline(pdf_path):
    pages = pdf_to_images(pdf_path)

    if SAVE_IMAGES and not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    full_text = ""

    for i, page in enumerate(pages):
        print(f"[INFO] Processing page {i+1}/{len(pages)}")

        processed = preprocess_image(page)

        if SAVE_IMAGES:
            cv2.imwrite(f"{IMAGE_DIR}/page_{i+1}.png", processed)

        text = extract_text(processed)

        full_text += f"\n--- PAGE {i+1} ---\n"
        full_text += text

    cleaned = clean_text(full_text)
    return cleaned


# -------------------------------
# SAVE OUTPUT
# -------------------------------
def save_text(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[INFO] OCR text saved to {path}")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    #pages = pdf_to_images(INPUT_PDF)
    result = ocr_pipeline(INPUT_PDF)
    save_text(result, OUTPUT_TEXT)