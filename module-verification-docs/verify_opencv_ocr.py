import os
import sys
from PIL import Image
from verification.utils import preprocess_image_for_ocr
from verification.ocr import extract_text_from_image

def verify_opencv_ocr(image_path):
    print(f"--- Verifying OCR Preprocessing for: {image_path} ---")
    
    if not os.path.exists(image_path):
        print(f"Error: File not found {image_path}")
        return

    # Load image
    img = Image.open(image_path)
    
    # Run OCR (which internally calls the updated preprocess_image_for_ocr)
    print("Extracting text with OpenCV preprocessing...")
    text = extract_text_from_image(image_path)
    
    print("\nEXTRACTED TEXT:")
    print("-" * 30)
    if text:
        print(text)
    else:
        print("[No text extracted or error occurred]")
    print("-" * 30)

    # Save preprocessed image for visual check
    processed_img = preprocess_image_for_ocr(img)
    debug_path = "debug_preprocessed.png"
    processed_img.save(debug_path)
    print(f"\nPreprocessed image saved to: {debug_path}")

if __name__ == "__main__":
    # Test with one of the existing CIN images
    sample_image = "docs/CIN.png" 
    verify_opencv_ocr(sample_image)
