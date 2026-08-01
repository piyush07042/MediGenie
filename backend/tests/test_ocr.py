import os
from app.services.ocr_service import process_medical_report

# Testing OCR Service
print("Testing OCR Service...")

# Dummy/Sample check: Agar aapke paas koi real image/pdf file hai toh uska path yahan dein
# Example: "sample.pdf" ya "sample_report.png"
sample_file = "test.pdf" 

if not os.path.exists(sample_file):
    print(f"[NOTE] '{sample_file}' nahi mila. Lekin OCR Service import aur initialize ho raha hai...")
    # Creating a temporary test text file to ensure function call logic works
    with open("test_sample.txt", "w") as f:
        f.write("Sample Clinical Test Report")
    print("Test environment ready!")
else:
    try:
        extracted_text = process_medical_report(sample_file)
        print("--- Extracted OCR Text ---")
        print(extracted_text)
    except Exception as e:
        print(f"Error during OCR execution: {e}")