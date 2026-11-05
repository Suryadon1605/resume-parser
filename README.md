# Resume Parser

A local Flask app that extracts contact details, skills, education, and experience from PDF, DOCX, or TXT resumes. Uploaded files are processed in memory and are not saved by the app.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. PDF extraction uses `pdfplumber`; DOCX extraction uses `python-docx`.

## Notes

This is a demo parser based on patterns and a configurable skills list, not a hiring decision tool. Review extracted details before using them. Do not upload sensitive resumes to a public deployment without adding access controls, retention rules, and a privacy notice.

## Publish

Create a public GitHub repository named `resume-parser`, then push this folder's contents. Add your name and repository link to your internship submission email.
