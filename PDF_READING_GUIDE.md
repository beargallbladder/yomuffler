# PDF Reading Guide for Claude

This guide explains how to work with PDF files and make them readable for Claude AI assistance.

## 🚀 Quick Start

### Step 1: Add a PDF to your workspace
```bash
# Copy or move your PDF file to the workspace
cp /path/to/your/document.pdf .
```

### Step 2: Extract text for Claude
```bash
# Use the helper script to extract text
python3 claude_pdf_helper.py document.pdf
```

### Step 3: Read the extracted text
The extracted text will be saved in `extracted_pdfs/document_extracted.txt` and you can ask Claude to read it.

## 📚 Available Tools

### 1. `pdf_reader.py` - Advanced PDF Text Extraction
A comprehensive tool with multiple extraction methods:

```bash
# Basic usage
python3 pdf_reader.py document.pdf

# Specify extraction method
python3 pdf_reader.py document.pdf -m pdfplumber

# Save to specific location
python3 pdf_reader.py document.pdf -o my_extracted_text.txt

# Export as JSON with metadata
python3 pdf_reader.py document.pdf --json
```

**Available extraction methods:**
- `auto` (default) - Tries all methods and returns the best result
- `pypdf2` - Good for simple text extraction
- `pdfplumber` - Better for tables and structured layouts
- `pymupdf` - Good for complex layouts and formatting
- `pdfminer` - Robust text extraction with good accuracy

### 2. `claude_pdf_helper.py` - Optimized for Claude
A simplified tool that extracts text and formats it for Claude:

```bash
# Extract PDF for Claude reading
python3 claude_pdf_helper.py document.pdf
```

This creates a file in `extracted_pdfs/` that Claude can easily read.

## 🔧 Installation

The necessary libraries are already installed in your environment:
- `PyPDF2` - Basic PDF text extraction
- `pdfplumber` - Advanced text and table extraction
- `pymupdf` - Comprehensive PDF processing
- `pdfminer.six` - Robust text extraction

## 📖 How to Use with Claude

### Method 1: Quick Extraction
```bash
# Extract PDF text
python3 claude_pdf_helper.py my_document.pdf

# The script will output: "✓ Ready for Claude! Use: read_file extracted_pdfs/my_document_extracted.txt"
```

### Method 2: Advanced Extraction
```bash
# Try different extraction methods if the first doesn't work well
python3 pdf_reader.py my_document.pdf -m pdfplumber
python3 pdf_reader.py my_document.pdf -m pymupdf
```

### Method 3: Direct Integration
You can also ask Claude to run the extraction process directly:
- "Please extract text from this PDF file: document.pdf"
- "Use the PDF helper to extract text from report.pdf"

## 🎯 Best Practices

### For Different PDF Types:

**Simple text documents:**
```bash
python3 pdf_reader.py document.pdf -m pypdf2
```

**Documents with tables/forms:**
```bash
python3 pdf_reader.py document.pdf -m pdfplumber
```

**Complex layouts/graphics:**
```bash
python3 pdf_reader.py document.pdf -m pymupdf
```

**Scanned documents (OCR needed):**
Note: These tools work with text-based PDFs. For scanned documents, you'd need OCR tools like Tesseract.

### File Organization:
```
workspace/
├── document.pdf                           # Original PDF
├── extracted_pdfs/                        # Extracted text files
│   └── document_extracted.txt
├── pdf_reader.py                          # Advanced extraction tool
└── claude_pdf_helper.py                   # Claude-optimized tool
```

## 🔍 Troubleshooting

### Common Issues:

**1. "Command not found: python3"**
```bash
# Try with python instead
python pdf_reader.py document.pdf
```

**2. "No module named 'PyPDF2'"**
```bash
# Reinstall PDF libraries
python3 -m pip install PyPDF2 pdfplumber pymupdf pdfminer.six
```

**3. "Permission denied"**
```bash
# Make scripts executable
chmod +x pdf_reader.py claude_pdf_helper.py
```

**4. "Extraction failed with all methods"**
- The PDF might be password protected
- The PDF might be scanned images (needs OCR)
- The PDF might be corrupted

### Getting Help:
```bash
# View help for the main tool
python3 pdf_reader.py --help

# View available extraction methods
python3 pdf_reader.py document.pdf -m auto
```

## 🎉 Examples

### Example 1: Extract a Research Paper
```bash
# Extract research paper with table support
python3 pdf_reader.py research_paper.pdf -m pdfplumber

# Claude can then read: extracted_pdfs/research_paper_extracted.txt
```

### Example 2: Extract Multiple PDFs
```bash
# Extract all PDFs in directory
for pdf in *.pdf; do
    python3 claude_pdf_helper.py "$pdf"
done
```

### Example 3: Export with Metadata
```bash
# Get extraction details as JSON
python3 pdf_reader.py document.pdf --json

# Creates: document_extracted.json with metadata
```

## 📊 Supported Features

✅ **Text extraction** from text-based PDFs  
✅ **Table extraction** (with pdfplumber)  
✅ **Multiple extraction methods** for compatibility  
✅ **Automatic method selection** for best results  
✅ **JSON export** with metadata  
✅ **Batch processing** support  
✅ **Claude-optimized** formatting  

❌ **OCR** for scanned documents (requires additional tools)  
❌ **Image extraction** (text only)  
❌ **Password-protected** PDFs  

## 🚀 Advanced Usage

### Custom Processing Script
```python
from pdf_reader import extract_pdf_text

# Extract text programmatically
text = extract_pdf_text("document.pdf", method="pdfplumber")
print(f"Extracted {len(text)} characters")

# Process text further
lines = text.split('\n')
filtered_lines = [line for line in lines if len(line) > 10]
```

### Batch Processing
```bash
# Process multiple PDFs at once
find . -name "*.pdf" -exec python3 claude_pdf_helper.py {} \;
```

---

## 🎯 Summary

To have Claude read your PDFs:

1. **Add PDF to workspace**: Copy your PDF file to the current directory
2. **Run extraction**: `python3 claude_pdf_helper.py your_document.pdf`
3. **Ask Claude to read**: The extracted text file will be in `extracted_pdfs/`

The tools are now ready to use! You can start working with PDFs immediately. 