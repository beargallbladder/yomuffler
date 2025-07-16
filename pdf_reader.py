#!/usr/bin/env python3
"""
PDF Text Extraction Tool
Extracts text from PDF files using multiple libraries for best compatibility
"""

import os
import sys
import argparse
from pathlib import Path
import json

# PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    import fitz  # PyMuPDF
    from pdfminer.high_level import extract_text
except ImportError as e:
    print(f"Error importing PDF libraries: {e}")
    print("Run: python3 -m pip install PyPDF2 pdfplumber pymupdf pdfminer.six")
    sys.exit(1)

def extract_with_pypdf2(pdf_path):
    """Extract text using PyPDF2"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")
        return None

def extract_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber (better for tables and layout)"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"pdfplumber extraction failed: {e}")
        return None

def extract_with_pymupdf(pdf_path):
    """Extract text using PyMuPDF (good for complex layouts)"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"PyMuPDF extraction failed: {e}")
        return None

def extract_with_pdfminer(pdf_path):
    """Extract text using pdfminer.six"""
    try:
        return extract_text(pdf_path).strip()
    except Exception as e:
        print(f"pdfminer extraction failed: {e}")
        return None

def extract_pdf_text(pdf_path, method="auto"):
    """
    Extract text from PDF using specified method or auto-detect best method
    
    Args:
        pdf_path: Path to PDF file
        method: Extraction method ('auto', 'pypdf2', 'pdfplumber', 'pymupdf', 'pdfminer')
    
    Returns:
        Extracted text content
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    extractors = {
        'pypdf2': extract_with_pypdf2,
        'pdfplumber': extract_with_pdfplumber,
        'pymupdf': extract_with_pymupdf,
        'pdfminer': extract_with_pdfminer
    }
    
    if method != "auto" and method in extractors:
        return extractors[method](pdf_path)
    
    # Auto mode: try all methods and return the best result
    results = {}
    for name, extractor in extractors.items():
        print(f"Trying {name}...")
        text = extractor(pdf_path)
        if text:
            results[name] = text
            print(f"✓ {name}: {len(text)} characters extracted")
        else:
            print(f"✗ {name}: Failed")
    
    if not results:
        raise Exception("All extraction methods failed")
    
    # Return the longest extracted text (usually the most complete)
    best_result = max(results.items(), key=lambda x: len(x[1]))
    print(f"\nBest result: {best_result[0]} ({len(best_result[1])} characters)")
    return best_result[1]

def save_extracted_text(text, output_path):
    """Save extracted text to file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Text saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF files')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('-o', '--output', help='Output text file path')
    parser.add_argument('-m', '--method', choices=['auto', 'pypdf2', 'pdfplumber', 'pymupdf', 'pdfminer'], 
                        default='auto', help='Extraction method')
    parser.add_argument('--json', action='store_true', help='Output as JSON with metadata')
    
    args = parser.parse_args()
    
    try:
        # Extract text
        print(f"Extracting text from: {args.pdf_path}")
        text = extract_pdf_text(args.pdf_path, args.method)
        
        # Prepare output
        if args.output:
            output_path = args.output
        else:
            pdf_name = Path(args.pdf_path).stem
            output_path = f"{pdf_name}_extracted.txt"
        
        if args.json:
            # Save as JSON with metadata
            data = {
                "source_file": args.pdf_path,
                "extraction_method": args.method,
                "text_length": len(text),
                "content": text
            }
            output_path = output_path.replace('.txt', '.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"JSON data saved to: {output_path}")
        else:
            # Save as plain text
            save_extracted_text(text, output_path)
        
        # Print preview
        print(f"\n--- Text Preview (first 500 characters) ---")
        print(text[:500])
        if len(text) > 500:
            print("...")
            print(f"\n[Total length: {len(text)} characters]")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 