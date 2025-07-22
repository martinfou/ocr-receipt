#!/usr/bin/env python3
"""
OCR Engine Example

This script demonstrates the usage of the OCR Engine for PDF processing.
It shows how to extract text from PDF files with confidence scoring.
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocr_receipt.core.ocr_engine import OCREngine, OCREngineError
from ocr_receipt.core.text_extractor import TextExtractor, TextExtractorError


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_sample_config():
    """Create a sample configuration for the OCR engine."""
    return {
        'ocr': {
            'language': 'eng',
            'confidence_threshold': 0.6,
            'tesseract_config': '--psm 6',
            'batch_size': 5,
            'enable_parallel': False
        },
        'image_processing': {
            'dpi': 300,
            'quality': 95,
            'format': 'PNG',
            'enable_noise_reduction': True,
            'enable_contrast_enhancement': True,
            'enable_deskew': True,
            'min_image_size': 100
        },
        'text_extraction': {
            'enable_preprocessing': True,
            'enable_enhancement': False,
            'min_confidence': 0.6,
            'max_retries': 3
        }
    }


def demonstrate_ocr_engine(pdf_path: str):
    """Demonstrate OCR engine functionality."""
    print("=" * 60)
    print("OCR Engine Demonstration")
    print("=" * 60)
    
    # Create configuration
    config = create_sample_config()
    
    try:
        # Initialize OCR engine
        print("\n1. Initializing OCR Engine...")
        ocr_engine = OCREngine(config)
        print("✓ OCR Engine initialized successfully")
        
        # Validate PDF file
        print(f"\n2. Validating PDF file: {pdf_path}")
        if ocr_engine.validate_pdf_file(pdf_path):
            print("✓ PDF file is valid")
        else:
            print("✗ PDF file is invalid or inaccessible")
            return
        
        # Get page count
        print("\n3. Getting PDF page count...")
        page_count = ocr_engine.get_pdf_page_count(pdf_path)
        print(f"✓ PDF has {page_count} pages")
        
        # Extract text from all pages
        print("\n4. Extracting text from all pages...")
        pages_data = ocr_engine.extract_text_from_all_pages(pdf_path)
        print(f"✓ Successfully processed {len(pages_data)} pages")
        
        # Display results for each page
        for page_num, text, confidence in pages_data:
            print(f"\n   Page {page_num}:")
            print(f"   - Confidence: {confidence:.2f}")
            print(f"   - Text length: {len(text)} characters")
            print(f"   - Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Get overall statistics
        print("\n5. Overall statistics:")
        confidence_scores = [confidence for _, _, confidence in pages_data]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        total_text_length = sum(len(text) for _, text, _ in pages_data)
        
        print(f"   - Average confidence: {avg_confidence:.2f}")
        print(f"   - Total text length: {total_text_length} characters")
        print(f"   - Pages with acceptable confidence: {sum(1 for c in confidence_scores if c >= 0.6)}")
        
        # Demonstrate single page extraction
        if page_count > 0:
            print(f"\n6. Extracting text from page 1...")
            page_text, page_confidence = ocr_engine.extract_text_from_pdf_page_with_confidence(pdf_path, 1)
            print(f"   - Page 1 confidence: {page_confidence:.2f}")
            print(f"   - Page 1 text preview: {page_text[:100]}{'...' if len(page_text) > 100 else ''}")
        
    except OCREngineError as e:
        print(f"✗ OCR Engine error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demonstrate_text_extractor(pdf_path: str):
    """Demonstrate Text Extractor functionality."""
    print("\n" + "=" * 60)
    print("Text Extractor Demonstration")
    print("=" * 60)
    
    # Create configuration
    config = create_sample_config()
    
    try:
        # Initialize Text Extractor
        print("\n1. Initializing Text Extractor...")
        text_extractor = TextExtractor(config)
        print("✓ Text Extractor initialized successfully")
        
        # Get PDF information
        print(f"\n2. Getting PDF information...")
        pdf_info = text_extractor.get_pdf_info(pdf_path)
        print(f"   - File path: {pdf_info['file_path']}")
        print(f"   - Page count: {pdf_info['page_count']}")
        print(f"   - Overall confidence: {pdf_info['overall_confidence']:.2f}")
        
        # Validate extraction quality
        print("\n3. Validating extraction quality...")
        quality_metrics = text_extractor.validate_extraction_quality(pdf_path)
        print(f"   - Total pages: {quality_metrics['total_pages']}")
        print(f"   - Successful pages: {quality_metrics['successful_pages']}")
        print(f"   - Failed pages: {quality_metrics['failed_pages']}")
        print(f"   - Average confidence: {quality_metrics['average_confidence']:.2f}")
        print(f"   - Quality score: {quality_metrics['quality_score']:.2f}")
        print(f"   - Total characters: {quality_metrics['total_characters']}")
        
        # Extract text with retry
        print("\n4. Extracting text with retry logic...")
        text = text_extractor.extract_with_retry(pdf_path, max_retries=2)
        print(f"   - Extracted text length: {len(text)} characters")
        print(f"   - Text preview: {text[:200]}{'...' if len(text) > 200 else ''}")
        
    except TextExtractorError as e:
        print(f"✗ Text Extractor error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def main():
    """Main function to run the OCR engine demonstration."""
    setup_logging()
    
    # Check if PDF path is provided
    if len(sys.argv) != 2:
        print("Usage: python ocr_engine_example.py <path_to_pdf>")
        print("\nExample:")
        print("  python ocr_engine_example.py /path/to/invoice.pdf")
        return
    
    pdf_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' does not exist.")
        return
    
    # Check if file is a PDF
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: File '{pdf_path}' is not a PDF file.")
        return
    
    print(f"Processing PDF: {pdf_path}")
    
    # Demonstrate OCR Engine
    demonstrate_ocr_engine(pdf_path)
    
    # Demonstrate Text Extractor
    demonstrate_text_extractor(pdf_path)
    
    print("\n" + "=" * 60)
    print("Demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    main() 