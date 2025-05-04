import re
from DataObjects.Book import Book
from Defs.Defs import EDITION_MARKERS, PUBLISHING_MARKERS

def extract_literature(raw_text: str):
    literature_entries = []
    entries = re.split(r'\n\s*\n|(?<=\d{4}[,:])\s*\n', raw_text.strip())

    for entry in entries:
        lit_obj = {
            "title": "",
            "year": "",
            "author": "",
            "edition": "",
            "isbn": "",
            "pubFirm": ""
        }

        # Extract ISBN
        isbn_match = re.search(r'ISBN\s*[-:\s]*([0-9\-]+)', entry, re.IGNORECASE)
        if isbn_match:
            lit_obj["isbn"] = isbn_match.group(1).strip()

        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', entry)
        if year_match:
            lit_obj["year"] = year_match.group(0)

        # Extract edition (match number followed by any edition marker)
        edition_regex = r'(\d+)\.?\s*(?:' + '|'.join(re.escape(m) for m in EDITION_MARKERS) + r')'
        edition_match = re.search(edition_regex, entry, re.IGNORECASE)
        if edition_match:
            lit_obj["edition"] = edition_match.group(1)

        # Extract publishing firm
        for pub in PUBLISHING_MARKERS:
            if pub.lower() in entry.lower():
                lit_obj["pubFirm"] = pub
                break

        # Extract author
        author_match = re.match(r'^(.+?)(:|“|")', entry)
        if author_match:
            lit_obj["author"] = author_match.group(1).strip()
        else:
            lit_obj["author"] = entry.split(":")[0].strip()

        # Extract title
        title_match = re.search(r':\s*[“"]?(.+?)(?:”|\"|,|\.|\d{4})', entry)
        if title_match:
            lit_obj["title"] = title_match.group(1).strip()

        if lit_obj["title"] or lit_obj["author"]:
            literature_entries.append(lit_obj)

    return {"literature": literature_entries}