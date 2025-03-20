import pymupdf
import pymupdf4llm
import pathlib
from io import StringIO
import pdfminer
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import re

def scrape_pdf_pymu(file_name):
    # md_text = pymupdf4llm.to_markdown(file_name)
    # pathlib.Path("catalog.md").write_bytes(md_text.encode())

    doc = pymupdf.open(file_name)
    full_text = []

    for page in doc:
        text = page.get_text("text").strip()
        
        if full_text:
            full_text.append("\n\n---\n\n")  # Add a page break separator
        
        full_text.append(text)

    combined_text = "\n".join(full_text)  # Combine all pages correctly

    # Save combined text as Markdown using PyMuPDF4llm (requires file input)
    # Temporary solution: Save raw text to file, then convert to markdown
    text_file_path = pathlib.Path("catalog_text_spring2015.txt")
    text_file_path.write_text(combined_text, encoding="utf-8")

scrape_pdf_pymu('environment/spring_2015_Course_Descriptions.pdf')

