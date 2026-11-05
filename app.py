from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from flask import Flask, render_template_string, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

SKILLS = [
    "Python", "Java", "JavaScript", "C++", "SQL", "HTML", "CSS", "React",
    "Flask", "Django", "FastAPI", "Machine Learning", "Deep Learning", "NLP",
    "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Git", "Docker",
    "AWS", "Azure", "Linux", "Excel", "Power BI", "Tableau", "PostgreSQL",
    "MongoDB", "REST API", "Communication", "Leadership", "Project Management",
]
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d ().-]{7,}\d)(?!\w)")
EDU_RE = re.compile(r"\b(?:B\.?Tech|B\.?E\.?|M\.?Tech|M\.?E\.?|B\.?Sc|M\.?Sc|MBA|Ph\.?D|Bachelor(?:'s)?|Master(?:'s)?| diploma)\b[^\n]{0,90}", re.I)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:present|current|(?:19|20)\d{2})\b", re.I)

PAGE = """<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Resume Parser</title><style>
body{font:16px system-ui;background:#f3f6fb;color:#172033;margin:0}.wrap{max-width:850px;margin:48px auto;padding:0 20px}.card{background:white;border:1px solid #dfe6f0;border-radius:16px;padding:28px;margin:18px 0;box-shadow:0 8px 28px #192c4d0a}h1{margin:0 0 8px}.muted{color:#5b6678}input,button{font:inherit}button{background:#245de3;color:white;border:0;border-radius:9px;padding:11px 18px;cursor:pointer}input[type=file]{margin:15px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.pill{display:inline-block;background:#edf2ff;padding:5px 10px;border-radius:20px;margin:4px}.err{color:#b42318}@media(max-width:650px){.grid{grid-template-columns:1fr}}
</style><div class='wrap'><h1>Resume Parser</h1><p class='muted'>Extract candidate details from PDF, DOCX, or TXT files. Files are processed in memory.</p>
<div class='card'><form method='post' enctype='multipart/form-data'><label for='resume'><b>Choose a resume</b></label><br><input id='resume' name='resume' type='file' accept='.pdf,.docx,.txt' required><br><button>Parse resume</button></form>{% if error %}<p class='err'>{{ error }}</p>{% endif %}</div>
{% if result %}<div class='card'><h2>Extracted profile</h2><div class='grid'><section><h3>Contact</h3><p><b>Email:</b> {{ result.email or 'Not found' }}</p><p><b>Phone:</b> {{ result.phone or 'Not found' }}</p><h3>Education</h3>{% for item in result.education %}<p>{{ item }}</p>{% else %}<p class='muted'>No education pattern found.</p>{% endfor %}</section><section><h3>Skills</h3>{% for item in result.skills %}<span class='pill'>{{ item }}</span>{% else %}<p class='muted'>No listed skills found.</p>{% endfor %}<h3>Experience dates</h3>{% for item in result.experience %}<p>{{ item }}</p>{% else %}<p class='muted'>No date ranges found.</p>{% endfor %}</section></div></div>{% endif %}</div></html>"""


def extract_text(filename: str, payload: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".txt":
        return payload.decode("utf-8", errors="replace")
    if ext == ".pdf":
        import pdfplumber
        with pdfplumber.open(BytesIO(payload)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    if ext == ".docx":
        from docx import Document
        doc = Document(BytesIO(payload))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Please upload a PDF, DOCX, or TXT file.")


def parse_resume(text: str) -> dict:
    found = {s.casefold(): s for s in SKILLS if re.search(r"(?<!\w)" + re.escape(s) + r"(?!\w)", text, re.I)}
    return {
        "email": next(iter(EMAIL_RE.findall(text)), ""),
        "phone": next(iter(PHONE_RE.findall(text)), ""),
        "skills": sorted(found.values(), key=str.casefold),
        "education": list(dict.fromkeys(m.group(0).strip(" .") for m in EDU_RE.finditer(text)))[:8],
        "experience": list(dict.fromkeys(m.group(0) for m in YEAR_RE.finditer(text)))[:8],
    }


@app.route("/", methods=["GET", "POST"])
def index():
    error, result = "", None
    if request.method == "POST":
        upload = request.files.get("resume")
        if not upload or not upload.filename:
            error = "Choose a file first."
        else:
            try:
                result = parse_resume(extract_text(upload.filename, upload.read()))
            except Exception as exc:
                error = str(exc) if isinstance(exc, ValueError) else "Could not read this file. Check that it is a valid PDF or DOCX."
    return render_template_string(PAGE, error=error, result=result)


if __name__ == "__main__":
    app.run(debug=False)
