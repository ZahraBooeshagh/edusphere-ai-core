!pip install pdfplumber sumy nltk

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
pdf_files = [
    "dwr-25-40-1.pdf"
]
import pdfplumber

def extract_pdf_text(pdf_path):
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                all_text += page_text + "\n"
    return all_text

print(extract_pdf_text(pdf_files[0])[:2001])


import re

def split_into_sections(all_text):
    section_pattern = r"\n([A-Z][A-Z\s\-&]+)\n"
    parts = re.split(section_pattern, all_text)
    sections = []
    for i in range(1, len(parts), 2):
        section_name = parts[i].strip().title()
        section_content = parts[i+1].strip()
        if len(section_content.split()) > 15:
            sections.append({
                "section": section_name,
                "content": section_content
            })
    return sections

all_text = extract_pdf_text(pdf_files[0])
sections = split_into_sections(all_text)
for s in sections[:3]:
    print(f"Section: {s['section']}")
    print(s['content'][:300])
    print("---")

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

def summarize_sections(sections, sentences_per_section=3):
    summarizer = LexRankSummarizer()
    summaries = []
    for section in sections:
        parser = PlaintextParser.from_string(section['content'], Tokenizer('english'))
        summary_sentences = [str(sent) for sent in summarizer(parser.document, sentences_per_section)]
        summaries.append({
            "section": section['section'],
            "summary": summary_sentences
        })
    return summaries

section_summaries = summarize_sections(sections)
for s in section_summaries:
    print(f"Section: {s['section']}")
    for sent in s['summary']:
        print(f"- {sent}")
    print()

def extract_tables_from_pdf(pdf_path):
    tables_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for pg_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for tbl_num, table in enumerate(tables, start=1):
                tables_data.append({
                    "page": pg_num,
                    "table_number": tbl_num,
                    "table": table
                })
    return tables_data

tables = extract_tables_from_pdf(pdf_files[0])
for t in tables[:3]:
    print(f"Page: {t['page']} | Table: {t['table_number']}")
    for row in t['table']:
        print(row)
    print("---")



import json

def process_all_pdfs(pdf_list):
    all_data = []
    for pdf_path in pdf_list:
        text = extract_pdf_text(pdf_path)
        sections = split_into_sections(text)
        summaries = summarize_sections(sections)
        tables = extract_tables_from_pdf(pdf_path)
        all_data.append({
            "source_file": pdf_path,
            "sections": summaries,
            "tables": tables
        })
    return all_data

standardized_data = process_all_pdfs(pdf_files)

for file_data in standardized_data:
    print(f"File: {file_data['source_file']} | Sections: {len(file_data['sections'])} | Tables: {len(file_data['tables'])}")

with open("standardized_course_data.json", "w", encoding="utf-8") as outfile:
    json.dump(standardized_data, outfile, ensure_ascii=False, indent=2)