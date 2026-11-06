# Resume Engine (`backend/resume_engine`)

## Overview
The Resume Engine is responsible for ingesting, parsing, segmenting, and evaluating candidate resumes in various file formats (PDF, DOCX, TXT, scanned images).

## Responsibilities
- **Multi-format Parsing**: Ingest raw text and layout metadata using PyMuPDF (`fitz`), `pdfplumber`, `python-docx`, and OCR via Tesseract.
- **Section Segmentation**: Heuristically and semantically segment resumes into standard blocks: Contact Information, Summary, Education, Work Experience, Skills, Certifications, and Projects.
- **ATS Compliance Auditing**: Analyze resume formatting, font consistency, structural parseability, and ATS red flags.
