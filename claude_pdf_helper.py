#!/usr/bin/env python3
"""
Claude PDF Helper
Quickly extract PDF text and save it in a format Claude can read
"""

import os
import sys
from pathlib import Path

# Import our PDF extraction functions
from pdf_reader import extract_pdf_text

def extract_pdf_for_claude(pdf_path, output_dir="extracted_pdfs"):
    """
    Extract PDF text and save it in a format optimized for Claude reading
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save extracted text files
    
    Returns:
        Path to the extracted text file
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract text
    print(f"Extracting text from: {pdf_path}")
    text = extract_pdf_text(pdf_path)
    
    # Create output filename
    pdf_name = Path(pdf_path).stem
    output_path = os.path.join(output_dir, f"{pdf_name}_extracted.txt")
    
    # Save text with some formatting for Claude
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Extracted from: {pdf_path}\n")
        f.write(f"# File size: {len(text)} characters\n")
        f.write(f"# Extraction date: {Path(pdf_path).stat().st_mtime}\n")
        f.write("\n" + "="*60 + "\n")
        f.write("EXTRACTED CONTENT:\n")
        f.write("="*60 + "\n\n")
        f.write(text)
    
    print(f"✓ Text extracted and saved to: {output_path}")
    print(f"✓ File contains {len(text)} characters")
    
    return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 claude_pdf_helper.py <pdf_file>")
        print("Example: python3 claude_pdf_helper.py document.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        output_path = extract_pdf_for_claude(pdf_path)
        print(f"\n✓ Ready for Claude! Use: read_file {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 