from setuptools import setup, find_packages

setup(
    name="ocr-receipt",
    version="0.1.0",
    description="A desktop application to extract structured data from PDF receipts using OCR.",
    author="Martin Fournier",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt6",
        "pytesseract",
        "pdf2image",
        "opencv-python",
        "Pillow",
        "PyPDF2",
        "click",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "ocr_receipt=ocr_receipt.cli.main:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.9",
) 